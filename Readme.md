![image](https://github.com/user-attachments/assets/5feafcea-430c-42c7-85ab-e2cbbc5dff3c)

A conversational AI agent that helps users book appointments on Google Calendar through natural language chat.

## Features

- 🤖 Natural language understanding
- 📅 Google Calendar integration
- 💬 Real-time chat interface
- 🔍 Availability checking
- ⏰ Smart time slot suggestions
- ✅ Automatic booking confirmation

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Google Cloud Console account
- OpenAI API key

### 2. Google Calendar Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download credentials.json and place in project root

### 3. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd tailortalk

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 4. Environment Variables
```
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_CALENDAR_ID=your_email@gmail.com
PORT=8000
```

### 5. Running the Application

Terminal 1 - Start Backend:
```bash
python backend/api.py
```

Terminal 2 - Start Frontend:
```bash
streamlit run main.py
```

### 6. First Time Setup
- When you first run the app, it will open a browser for Google OAuth
- Grant calendar permissions
- The app will save your credentials for future use

## Usage Examples

- "Do you have any free time this Friday?"
- "I want to schedule a call for tomorrow afternoon"
- "Book a meeting between 3-5 PM next week"
- "What's available on Monday morning?"

## Architecture

- **Frontend**: Streamlit chat interface
- **Backend**: FastAPI with async endpoints
- **Agent**: LangGraph for conversation flow
- **Calendar**: Google Calendar API integration
- **LLM**: OpenAI GPT-3.5-turbo for natural language understanding

## Deployment

For production deployment, consider:
- Using a proper database for session management
- Implementing user authentication
- Setting up proper environment variable management
- Using a production WSGI server like Gunicorn
```

## How to Test and Run

### Step 1: Google Calendar Setup
1. Go to Google Cloud Console
2. Create new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download credentials.json

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Environment Variables
Create `.env` file with:
```
OPENAI_API_KEY=your_key_here
GOOGLE_CALENDAR_ID=your_email@gmail.com
```

### Step 4: Run the Application
Terminal 1:
```bash
python backend/api.py
```

Terminal 2:
```bash
streamlit run main.py
```

### Step 5: Test Conversations
Try these examples:
- "Do you have any free time this Friday?"
- "Book a meeting for tomorrow at 3 PM"
- "What's available next week?"

The app will handle OAuth authentication on first run and then provide a fully functional booking interface!


### Virtual Enviotnment
- python3 -m venv .venv
- . .venv/bin/activate
