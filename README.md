# LINE Chatbot

A LINE chatbot built with Python and LINE Bot SDK. It is an AI chatbot that can have conversations with users.

## Features

- Natural language conversation capabilities
- Integration with LINE messaging platform
- Docker support for easy deployment
- File upload handling
- Logging system for debugging and monitoring

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for containerized deployment)
- LINE Messaging API account
- LINE Channel Secret and Channel Access Token

## Installation

### Local Development

1. Clone the repository:
  ```bash
  git clone https://github.com/yourusername/line-chatbot.git
  cd line-chatbot
  ```

2. Create and activate a virtual environment:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  ```

3. Install required dependencies:
  ```bash
  pip install -r requirements.txt
  ```

4. Set up environment variables:
  ```bash
  cp .env_bak .env
  # Edit .env with your LINE credentials
  ```

### Docker Deployment

1. Build and run using Docker Compose:
  ```bash
  docker-compose up --build
  ```

## Configuration

1. Create a LINE Messaging API channel at [LINE Developers Console](https://developers.line.biz/console/)
2. Get your Channel Secret and Channel Access Token
3. Update the `.env` file with your credentials:
  ```
  OPENAI_API_KEY=your_openai_api_key
  LINE_CHANNEL_SECRET=your_channel_secret
  LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
  ```

## Usage

### Local Development

1. Start the server:
  ```bash
  python main.py
  ```

2. Set up your webhook URL in the LINE Developers Console to point to your server's endpoint
3. Start chatting with your bot on LINE!

### Docker Deployment

The application will be available at `http://localhost:8080` after running `docker-compose up`.

## Project Structure

```
line-chatbot/
├── main.py              # Main application file
├── chatbot.py           # Chatbot logic implementation
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── .env_bak           # Environment variables template
├── uploads/           # Directory for uploaded files
└── README.md         # Project documentation
```

## Development

- The application uses a modular structure with `main.py` handling the web server and `chatbot.py` containing the chatbot logic
- Logs are stored in the `logs/` directory
- Uploaded files are stored in the `uploads/` directory

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.