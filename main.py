from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, ImageMessage, FlexMessage, PushMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent
from flask import Flask, request, abort, jsonify
import requests
import os
from datetime import datetime

import threading
from collections import defaultdict

from chatbot import chitchat as CHAT

# Initialize the Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# LINE Channel Access Token and Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# Initialize LINE API and Webhook handler
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def download_line_image(event):
    try:
        headers = {'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'}
        content_url = f'https://api-data.line.me/v2/bot/message/{event.message.id}/content'
        
        response = requests.get(content_url, headers=headers)
        response.raise_for_status()

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_id = event.source.user_id if hasattr(event.source, 'user_id') else 'unknown'
        filename = f"image_{user_id}_{timestamp}_{event.message.id}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the image
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # print(f"Image saved: {filepath}")
        return filename, filepath
    except Exception as e:
        print(f"Error downloading LINE image: {e}", flush=True)
        return None

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
    response = CHAT(user_message, user_id)
    # print("==="*20)
    # print("Response:", response)
    # print("==="*20)
    
    text_message = TextMessage(text=response)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # # get user name
        # user_profile = line_bot_api.get_profile(user_id)
        # user_name = user_profile.display_name
        line_bot_api.reply_message_with_http_info(ReplyMessageRequest(reply_token=event.reply_token, messages=[text_message]))
            
# Dictionary to track user's image batches
user_image_batches = defaultdict(list)
user_timers = {}
BATCH_DELAY = 3  # seconds to wait for more images
def send_batch_response(event):
    """Send a single response for all images in the batch"""
    user_id = event.source.user_id if hasattr(event.source, 'user_id') else 'unknown'
    try:
        if user_id not in user_image_batches or not user_image_batches[user_id]:
            return
            
        batch_info = user_image_batches[user_id]
        image_count = len(batch_info)
        
        # if image_count == 1:
        #     message_text = f"Image received and saved successfully! ✅\nFilename: {batch_info[0]['filename']}"
        # else:
        #     filenames = "\n".join([f"• {info['filename']}" for info in batch_info])
        #     message_text = f"{image_count} images received and saved successfully! ✅\n\nFilenames:\n{filenames}"
        
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"Thank you for you images. (^.^)")]
                )
            )
            
        # Clear the batch after sending response
        user_image_batches[user_id] = []
        if user_id in user_timers:
            del user_timers[user_id]
            
        # print(f"Batch response sent to {user_id} for {image_count} images")
        
    except Exception as e:
        print(f"Error sending batch response: {e}", flush=True)

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image(event):
    user_id = event.source.user_id if hasattr(event.source, 'user_id') else 'unknown'
    try:
        filename, filepath = download_line_image(event)
        # Add to user's batch
        user_image_batches[user_id].append({
            'filename': filename,
            'filepath': filepath,
            'timestamp': datetime.now()
        })
        
        # Cancel existing timer if any
        if user_id in user_timers:
            user_timers[user_id].cancel()
        
        # Set new timer for batch response
        timer = threading.Timer(BATCH_DELAY, send_batch_response, args=[event])
        user_timers[user_id] = timer
        timer.start()
        
    except Exception as e:
        print(f"Error handling LINE image: {e}", flush=True)
        # Send error message
        text_message = TextMessage(text="Sorry, there was an error saving your image.")
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[text_message]
                )
            )
      
@app.route('/health', methods=['GET'])
def index():
    response = 'OK'
    return jsonify({'response': response})

if __name__ == "__main__":
    # Run the Flask app
    app.run(host='0.0.0.0', port=8080, debug=True)
    