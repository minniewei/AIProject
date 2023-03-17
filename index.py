from flask import Flask, request, abort
from chatGPT import ChatGPT
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
# 為了處理json字串引入的模組
import json

app = Flask(__name__)
chatgpt = ChatGPT()
line_bot_api = LineBotApi('dw7F38Eky44laTlVAnBEW9JX9PH8vP4t2k3rQlLX1s4RYLmfce/L2K+g+cx3xEl0CztGTYeG9LLjhTwuxX3CZGKZx7OEhbW88OLhgGjv28E/L9WFgux7OCUQsmV45mHaNIQnLunqJAEs/wY3ix4n3wdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ed4533c06497af6784dda91261f6b100')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    #  想了解問題1: event的內容到底是甚麼
    print(event)
    if event.message.type != "text":
        return 
    if event.message.text == "啟動":
        working_status = True
        line_bot_api.reply_message(
            # 想了解問題2: reply_message的4參數到底是啥
            event.reply_token,
            TextSendMessage( text = "我是時下流行的AI智能，目前可為您服務囉，歡迎來跟我互動~")
        )
        return 
    if event.message.text == "安靜":
        working_status = False  
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage( text = "感謝您目前的使用，若需要我的服務，請跟我說啟動謝謝~")
        )
        return 
    if working_status :
        chatgpt.add_msg(f"Human:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg)
        )

if __name__ == "__main__":
    app.run()