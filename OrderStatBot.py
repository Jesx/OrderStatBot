from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

orders1 = []
orders2 = []
 
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

    # profile = line_bot_api.get_profile(user_id)
    # user_name = profile.display_name

    if text.startswith('/order1'):
        drink = text[8:]
        orders1.append(drink)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'已於 order1 記錄你的餐點品項：{drink}')
        )
    elif text.startswith('/order2'):
        food = text[8:]
        orders2.append(food)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'已於 order2 記錄你的餐點品項：{drink}')
        )
    elif text == '/stat1':
        if not orders1:
            msg = 'No orders in order1.'
        else:
            msg = '\n'.join([f'{i+1}. {drink}' for i, drink in enumerate(orders1)])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
        )
    elif text == '/stat2':
        if not orders1:
            msg = 'No orders in order2.'
        else:
            msg = '\n'.join([f'{i+1}. {food}' for i, food in enumerate(orders2)])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
        )
    elif text == '/clear1':
        orders1.clear()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Order list1 has been cleared.🗑️')
        )
    elif text == '/clear2':
        orders2.clear()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Order list2 has been cleared.🗑️')
        )
    elif text == '/clear':
        orders1.clear()
        orders2.clear()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Order lists have been cleared.🗑️')
        )

if __name__ == "__main__":
    app.run()