import requests
import os
from dotenv import load_dotenv
load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def create_rich_menu(channel_token=LINE_CHANNEL_ACCESS_TOKEN):
    url = f'https://api.line.me/v2/bot/richmenu'
    headers = {'Authorization': f'Bearer {channel_token}',
               'Content-Type': 'application/json'}
    data = {
    "size": {
        "width": 2500,
        "height": 1686
    },
    "selected": False,
    "name": "Test the default rich menu",
    "chatBarText": "Tap to open",
    "areas": [
        { # First area
            "bounds": {
                "x": 0,
                "y": 0,
                "width": 1250,
                "height": 250
            },
            "action": {
                "type": "message",
                "label": "Red tab",
                "text": "Red tab"
            }
        },
        { # Second area
            "bounds": {
                "x": 1251,
                "y": 0,
                "width": 1250,
                "height": 250
            },
            "action": {
                "type": "message",
                "label": "Green tab",
                "text": "Green tab"
            }
        },
        { # Third area
            "bounds": {
                "x": 0,
                "y": 251,
                "width": 1250,
                "height": 593
            },
            "action": {
                "type": "message",
                "label": "A tab",
                "text": "A tab"
            }
        },
        { # Fourth area
            "bounds": {
                "x": 1251,
                "y": 251,
                "width": 1250,
                "height": 593
            },
            "action": {
                "type": "message",
                "label": "B tab",
                "text": "B tab"
            }
        },
        { # Fifth area
            "bounds": {
                "x": 0,
                "y": 844,
                "width": 1250,
                "height": 843
            },
            "action": {
                "type": "message",
                "label": "C tab",
                "text": "C tab"
            }
        },
        { # Sixth area
            "bounds": {
                "x": 1251,
                "y": 844,
                "width": 1250,
                "height": 843
            },
            "action": {
                "type": "message",
                "label": "D tab",
                "text": "D tab"
            }
        },
    ]
}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Message sent successfully!")
        print(response.json())
    else:
        print(f"Failed to send message. Status: {response.status_code}, Response: {response.text}")

def upload_rich_menu_image(rich_menu_id, image_path, channel_token=LINE_CHANNEL_ACCESS_TOKEN):
    url = f'https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content'
    headers = {
        'Authorization': f'Bearer {channel_token}',
        'Content-Type': 'image/png'
    }
    with open(image_path, 'rb') as image_file:
        response = requests.post(url, headers=headers, data=image_file)
    if response.status_code == 200:
        print("Image uploaded successfully!")
    else:
        print(f"Failed to upload image. Status: {response.status_code}, Response: {response.text}")

def set_def_rich_menu(rich_menu_id, channel_token=LINE_CHANNEL_ACCESS_TOKEN):
    url = f'https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}'
    headers = {
        'Authorization': f'Bearer {channel_token}'
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print("Default rich menu set successfully!")
    else:
        print(f"Failed to set default rich menu. Status: {response.status_code}, Response: {response.text}")

def cancel_def_rich_menu(channel_token=LINE_CHANNEL_ACCESS_TOKEN):
    url = f'https://api.line.me/v2/bot/user/all/richmenu'
    headers = {
        'Authorization': f'Bearer {channel_token}'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        print("Default rich menu cancelled successfully!")
    else:
        print(f"Failed to cancel default rich menu. Status: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    # create_rich_menu()
    # upload_rich_menu_image('richmenu-980dfc7d28ac3df1a55496f4a588ffed', "richmenu-template-guide-02-mock.png")
    # set_def_rich_menu('richmenu-980dfc7d28ac3df1a55496f4a588ffed')
    cancel_def_rich_menu()