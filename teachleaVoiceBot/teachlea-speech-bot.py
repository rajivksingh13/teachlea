import streamlit as st
import openai
import speech_recognition as sr
from gtts import gTTS
# import os
from io import BytesIO
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv

# Load environment variables
# load_dotenv()
openai.api_key = st.secrets["OPEN_AI_KEY"]

# Initialize Streamlit
st.title("Voice-Enabled Chatbot")
st.info("Speak into your microphone to interact with the bot.")

# Initialize recognizer
recognizer = sr.Recognizer()

# Set up conversation history
chat_history = []

# Function to transcribe audio
def transcribe_audio(audio_data):
    try:
        with sr.AudioFile(audio_data) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except Exception as e:
        return f"Error transcribing audio: {e}"

# Function for text-to-speech
def speak(text):
    tts = gTTS(text, lang="en")
    audio_stream = BytesIO()
    tts.write_to_fp(audio_stream)
    audio_stream.seek(0)
    return audio_stream

# Voice input section
uploaded_audio = st.file_uploader("Upload your voice input (.wav only):", type="wav")
if uploaded_audio:
    st.info("Processing your voice input...")
    user_query = transcribe_audio(uploaded_audio)
    st.success(f"You said: {user_query}")

    # Process the query
    if user_query:
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai.api_key)
        prompt = PromptTemplate(
            input_variables=["chat_history", "user_input"],
            template="This is the chat history: {chat_history}. User says: {user_input}. Respond accordingly."
        )
        response = llm.generate_responses(
            [{"chat_history": chat_history, "user_input": user_query}]
        )
        reply = response[0].text
        st.write(f"Bot: {reply}")
        chat_history.append({"user": user_query, "bot": reply})

        # Play bot's response
        st.audio(speak(reply), format="audio/wav")
