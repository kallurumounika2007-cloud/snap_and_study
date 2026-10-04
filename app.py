import json

import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client as TwilioClient

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
)

MODEL_NAME = "gemini-3.5-flash"

st.set_page_config(
    page_title="Snap & Study",
    page_icon="Study",
    layout="wide",
)

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_FROM = st.secrets["TWILIO_WHATSAPP_FROM"]
TWILIO_CONTENT_SID = st.secrets["TWILIO_CONTENT_SID"]


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


@st.cache_resource
def get_twilio_client():
    return TwilioClient(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN
    )


gemini_client = get_gemini_client()
twilio_client = get_twilio_client()


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    message = {
        "role": role,
        "kind": kind,
        "content": content
    }

    st.session_state.messages.append(message)
    render_message(message)


def ask_gemini(parts):
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"


def clean_whatsapp_text(text):
    if not text:
        return "No study explanation available."

    text = " ".join(text.split())

    if len(text) > 1500:
        return text[:1500] + "..."

    return text


def send_whatsapp(to_number, user_name, summary):
    try:
        content_variables = json.dumps(
            {
                "1": user_name,
                "2": clean_whatsapp_text(summary)
            },
            ensure_ascii=False
        )

        message = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_number}",
            content_sid=TWILIO_CONTENT_SID,
            content_variables=content_variables,
        )

        return True, message.sid

    except Exception as error:
        return False, str(error)


if "onboarded" not in st.session_state:

    st.title("Snap & Study")

    st.caption("Your AI study tutor for problems, diagrams and notes.")

    st.write(
        "Upload a study image and get a step-by-step explanation."
    )

    with st.form("onboarding_form"):

        name = st.text_input(
            "Your name",
            placeholder="Enter your name"
        )

        whatsapp_number = st.text_input(
            "WhatsApp number with country code",
            placeholder="+91XXXXXXXXXX",
            help="Use the WhatsApp number that has joined your Twilio WhatsApp sandbox."
        )

        submitted = st.form_submit_button(
            "Start Studying"
        )

    if submitted:

        if not name.strip() or not whatsapp_number.strip():

            st.warning(
                "Please enter both your name and WhatsApp number."
            )

        else:

            st.session_state.name = name.strip()

            st.session_state.whatsapp_number = (
                whatsapp_number.strip()
            )

            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )

            st.session_state.messages = []

            st.session_state.onboarded = True

            st.rerun()

    st.stop()


header_col, button_col = st.columns(
    [5, 2],
    vertical_alignment="center"
)


with header_col:
    st.title("Snap & Study")
    st.caption("Your AI tutor for problems, diagrams and notes.")


with button_col:

    send_disabled = len(st.session_state.messages) <= 2

    if st.button(
        "Send Explanation to WhatsApp",
        disabled=send_disabled,
        use_container_width=True
    ):

        with st.spinner("Preparing your study notes..."):

            summary = ask_gemini(
                [SUMMARY_REQUEST_PROMPT]
            )

        success, info = send_whatsapp(
            st.session_state.whatsapp_number,
            st.session_state.name,
            summary
        )

        if success:
            st.success(
                "Study explanation sent to WhatsApp."
            )
        else:
            st.error(
                f"Couldn't send the explanation: {info}"
            )


st.caption(
    f"Student: {st.session_state.name} | "
    f"WhatsApp: {st.session_state.whatsapp_number}"
)


if not st.session_state.messages:

    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        )
    )

else:

    for message in st.session_state.messages:
        render_message(message)


user_input = st.chat_input(
    "Ask a question or upload a study image",
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png"
    ],
)


if user_input:

    photo = (
        user_input.files[0]
        if user_input.files
        else None
    )

    text = user_input.text

    parts = []

    if photo is not None:

        photo_bytes = photo.getvalue()

        add_message(
            "user",
            "image",
            photo_bytes
        )

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type
            )
        )

    if text:

        add_message(
            "user",
            "text",
            text
        )

        parts.append(text)

    elif photo is not None:

        parts.append(
            """
            Analyze this study image carefully.

            Identify the problem, diagram, notes,
            or concept shown.

            Explain it step by step in simple language.

            If it is a problem, solve it and explain
            why each step is performed.

            Highlight important formulas or concepts.
            """
        )

    with st.spinner("Analyzing..."):

        answer = ask_gemini(parts)

    add_message(
        "assistant",
        "text",
        answer
    )