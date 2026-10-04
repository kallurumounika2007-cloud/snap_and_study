# Snap & Study

Snap & Study is an AI-powered visual study tutor built with Streamlit and Gemini.

Students can upload photos of:
- Mathematical problems
- Programming questions
- Diagrams
- Handwritten notes
- Textbook pages
- Technical concepts

Gemini analyzes the uploaded image and explains the content step by step in simple language. Students can also ask follow-up questions within the same conversation.

The final study explanation can be sent to the student's WhatsApp using Twilio.

## Features

- AI-powered image understanding
- Step-by-step explanations
- Support for multiple academic subjects
- Conversational follow-up questions
- Study summary generation
- WhatsApp delivery using Twilio

## Tech Stack

- Python
- Streamlit
- Google Gemini
- Twilio WhatsApp

## Run Locally

### 1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL

cd Snap&Study

### 2. Create a virtual environment

python -m venv venv

### 3. Activate the environment

Windows:

venv\Scripts\activate

### 4. Install dependencies

pip install -r requirements.txt

### 5. Configure secrets

Create:

.streamlit/secrets.toml

Add your Gemini and Twilio credentials.

### 6. Run the application

streamlit run app.py

The application will open in your browser.

## Security

Never commit `.streamlit/secrets.toml`.

Only `.streamlit/secrets.toml.example` should be included in the repository.