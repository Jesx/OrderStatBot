from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import libsql_experimental as libsql
import sqlite3
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

def insert_order(user_id, category, drink):
    conn = libsql.connect(database=url, auth_token=auth_token)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (user_id, category, item)
        VALUES (?, ?, ?)
    ''', (user_id, category, drink))
    conn.commit()

def fetch_orders(category):
    conn = libsql.connect(database=url, auth_token=auth_token)
    cursor = conn.cursor()
    cursor.execute('SELECT item FROM orders WHERE category = ?', (category,))
    rows = cursor.fetchall()
    return rows

def delete_orders_by_category(category):
    conn = libsql.connect(database=url, auth_token=auth_token)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM orders WHERE category = ?', (category,))
    conn.commit()

def delete_orders():
    conn = libsql.connect(database=url, auth_token=auth_token)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM orders')
    conn.commit()
 
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    user_id = event.source.user_id

    if text.startswith('/order1'):
        drink = text[8:]
        insert_order(user_id, 1, drink)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'已於 order1 記錄你的餐點品項：{drink}')
        )
    elif text.startswith('/order2'):
        food = text[8:]
        insert_order(user_id, 2, food)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'已於 order2 記錄你的餐點品項：{food}')
        )
    elif text == '/stat1':
        orders1 = fetch_orders(1)
        if not orders1:
            msg = 'No orders in order1.'
        else:
            msg = '\n'.join([f'{i}. {drink}' for i, (drink,) in enumerate(orders1, 1)])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
        )
    elif text == '/stat2':
        orders2 = fetch_orders(2)
        if not orders2:
            msg = 'No orders in order2.'
        else:
            msg = '\n'.join([f'{i}. {food}' for i, (food,) in enumerate(orders2, 1)])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
        )
    elif text == '/clear1':
        delete_orders_by_category(1)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Order list1 has been cleared.🗑️')
        )
    elif text == '/clear2':
        delete_orders_by_category(2)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Order list2 has been cleared.🗑️')
        )
    elif text == '/clear':
        delete_orders()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Order lists have been cleared.🗑️')
        )

if __name__ == "__main__":
    app.run()
