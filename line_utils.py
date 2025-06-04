import requests
import os
from dotenv import load_dotenv
load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def reply_message_with_mention(user_id, reply_token, message_text, channel_token=LINE_CHANNEL_ACCESS_TOKEN):
    url = f'https://api.line.me/v2/bot/message/reply'
    headers = {'Authorization': f'Bearer {channel_token}'}
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "textV2",
                  "text": f"{{user1}} {message_text}",
                  "substitution": {
                      "user1": {
                          "type": "mention",
                          "mentionee": {
                              "type": "user",
                              "userId": user_id,
                          }
                      }
                }
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Status: {response.status_code}, Response: {response.text}")