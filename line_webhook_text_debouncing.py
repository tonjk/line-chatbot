from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, ImageMessage, FlexMessage, PushMessageRequest, ShowLoadingAnimationRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent
from linebot.v3.messaging.models import FlexContainer

from flask import Flask, request, abort, jsonify

import os
from time import time
# from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue
import time as time_module
import numpy as np

from dotenv import load_dotenv
load_dotenv()

# from src.chatbot.chatbot import BIOChatbot
from chatbot import chitchat as CHAT

from datetime import timedelta
from typing import Optional, Dict, Any

import logging

logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize the Flask app
app = Flask(__name__)

# LINE Channel Access Token and Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# Initialize LINE API and Webhook handler
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# # Thread pool executor for running synchronous operations
# executor = ThreadPoolExecutor(max_workers=10)


RESET_MESSAGE = "Hello! How can I help you today?"
ERROR_MESSAGE = "ขออภัยครับ เกิดข้อผิดพลาดในการประมวลผล กรุณาลองใหม่อีกครั้งครับ"

def send_line_message_sync(reply_token, messages):
    """Synchronous function to send LINE messages"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(ReplyMessageRequest(reply_token=reply_token, messages=messages))
            # logger.info("LINE message sent successfully")
    except Exception as e:
        print(f"Error sending LINE message: {e}", flush=True)
        logger.error(f"Error sending LINE message: {e}")

def get_user_profile_sync(user_id):
    """Synchronous function to get user profile"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            return line_bot_api.get_profile(user_id)
    except Exception:
        logger.exception("Failed to get profile for user %s", user_id)
        raise

def show_loading_animation_sync(user_id, loading_seconds=60):
    """Synchronous function to show loading animation"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.show_loading_animation(
                ShowLoadingAnimationRequest(chat_id=user_id, loading_seconds=loading_seconds)
            )
    except Exception:
        logger.exception("Failed to show loading animation for %s", user_id)

async def process_message_async(event):
    """Process a single message event using asyncio; wraps blocking calls in threads."""
    logger.info(f"Received message event {event}")
    input_type = event.message.type
    user_message = event.message.text if input_type == 'text' else 'check this image'
    user_id = event.source.user_id
    start_time = time()
    # logger.info(f"Received message from user {user_id}: {user_message}")

    lock = get_user_lock(user_id)
    async with lock:
        try:
            # Show loading animation (blocking SDK wrapped)
            await asyncio.to_thread(show_loading_animation_sync, user_id, 60)
            
            # Check if the user message is a reset command
            if user_message.strip().lower() == '#reset':
                await asyncio.to_thread(agent.clear_all, user_id)
                text_message = TextMessage(text=RESET_MESSAGE)
                await asyncio.to_thread(send_line_message_sync, event.reply_token, [text_message])
                response_for_log = {"response": text_message.text, "image_url": None}
            
            # add or no command
            elif user_message.strip().lower().startswith(('add', 'no')):
                log_type = 'add' if user_message.strip().lower().startswith('add') else 'no'
                help_message = "ขอบคุณสำหรับคำแนะนำครับ 😊"
                text_message = TextMessage(text=help_message)
                
                # Log
                # await asyncio.to_thread(log_add_info, user_id, user_name, event.message.id, log_type, user_message)
                
                await asyncio.to_thread(send_line_message_sync, event.reply_token, [text_message])
                response_for_log = {"response": text_message.text, "image_url": None}
            
            else:
                # Process with agent (now truly async)
                response, state = await agent.process_message(user_id=user_id,
                                                              input_type=input_type,
                                                              message=user_message,
                                                              image_url=["mockup"],
                                                              language="th", # "th", "my"
                )

                # handle error response that not contain 'response' key
                if 'response' not in response:
                    text_message = TextMessage(text=ERROR_MESSAGE)
                    await asyncio.to_thread(send_line_message_sync, event.reply_token, [text_message])
                    # response_for_log = {"response": str(response), "image_url": None}
                else:
                    text_message = TextMessage(text=response['response'])
                    await asyncio.to_thread(send_line_message_sync, event.reply_token, [text_message])
                    # response_for_log = {"response": response.get('response', ''), "image_url": response.get('image_url')}
            
                        
            end_time = time()
            resp_time = f"{end_time - start_time:.2f}"
            

        except Exception as e:
            print(f"Error processing message: {str(e)}")
            # Send error message to user
            error_message = TextMessage(text=ERROR_MESSAGE)
            try:
                await asyncio.to_thread(send_line_message_sync, event.reply_token, [error_message])
            except:
                pass


# response = CHAT(user_message, user_id)

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

from collections import defaultdict
user_text_batches = defaultdict(list)
user_timers = {}
TEXT_DEBOUNCE_SECONDS = 3 # seconds to wait for more text

def process_accumulated_text(event):
    user_id = event.source.user_id if hasattr(event.source, 'user_id') else 'unknown'
    try:
        if user_id not in user_text_batches or not user_text_batches[user_id]:
            return

        combined_text = "\n".join(user_text_batches[user_id])
        response_text = CHAT(combined_text, user_id)

        send_line_message_sync(event.reply_token, [TextMessage(text=response_text)])

        # Clear the batch after sending response
        user_text_batches[user_id] = []
        if user_id in user_timers:
            del user_timers[user_id]

    except Exception as e:
        print(f"Error processing accumulated text for {user_id}: {e}", flush=True)
    
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    user_id = event.source.user_id if hasattr(event.source, 'user_id') else 'unknown'
    user_text_batches[user_id].append(event.message.text)
    if user_id not in user_timers:
        timer = threading.Timer(TEXT_DEBOUNCE_SECONDS, process_accumulated_text, args=[event])
        user_timers[user_id] = timer
        timer.start()

if __name__ == "__main__":
    # Run the Flask app
    app.run(host='0.0.0.0', port=8080, debug=True)