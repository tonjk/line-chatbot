# Line OA - Fx Bot
# test quick reply

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, QuickReply, QuickReplyItem, MessageAction
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os

from flask import Flask, request, abort, jsonify

# Initialize the Flask app
app = Flask(__name__)

# LINE Channel Access Token and Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# Initialize LINE API and Webhook handler
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id

    
    with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            quick_reply_items = QuickReply(items=[
                 QuickReplyItem(action=MessageAction(label="Yes", text="Yes")),
                 QuickReplyItem(action=MessageAction(label="No", text="No")),
                 QuickReplyItem(action=MessageAction(label="OK", text="OK")),
                 ]
                 )
            line_bot_api.reply_message_with_http_info(ReplyMessageRequest(reply_token=event.reply_token,
                                                                          messages=[TextMessage(text=user_message + " + Pls select button.",
                                                                                                quick_reply=quick_reply_items)]))

@app.route('/health', methods=['GET'])
def index():
    response = 'OK'
    return jsonify({'response': response})

if __name__ == "__main__":
    # Run the Flask app
    app.run(host='0.0.0.0', port=8080, debug=True)
    