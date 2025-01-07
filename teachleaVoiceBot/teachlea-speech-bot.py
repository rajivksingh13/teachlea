import openai
import streamlit as st
import speech_recognition as sr
import pyttsx3
# from dotenv import load_dotenv
# import os

# Load environment variables
# load_dotenv()
# openai.api_key = st.secrets.get("OPEN_AI_KEY") or os.getenv("OPEN_AI_KEY")
openai.api_key = st.secrets["OPEN_AI_KEY"]
# Initialize TTS engine
tts_engine = pyttsx3.init()

def speak_text(text):
    """Converts text to speech."""
    tts_engine.say(text)
    tts_engine.runAndWait()

def recognize_speech_from_microphone():
    """Captures and transcribes voice input using the microphone."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    try:
        with mic as source:
            st.info("Listening... Please speak now.")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        st.info("Processing your voice input...")
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand your speech."
    except sr.RequestError as e:
        return f"Error with speech recognition service: {e}"

# Streamlit UI
st.title("Voice-Enabled Chatbot with OpenAI")

st.sidebar.header("Instructions")
st.sidebar.write("""
1. Click 'Record' to provide your input via voice.
2. The chatbot will respond with text and voice.
""")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat Input
st.header("Chat with AI")
user_input = st.text_input("Type your message or use voice input:")

if st.button("Record Voice Input"):
    user_input = recognize_speech_from_microphone()
    st.text(f"You said: {user_input}")

if user_input:
    # ChatGPT API call
    with st.spinner("Generating response..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input},
                ],
            )
            bot_response = response['choices'][0]['message']['content'].strip()
            st.session_state.chat_history.append((user_input, bot_response))

            # Display the response
            st.text_area("Chat History", value="\n".join(
                [f"User: {q}\nBot: {a}" for q, a in st.session_state.chat_history]), height=300)

            # Speak the response
            speak_text(bot_response)

        except Exception as e:
            st.error(f"An error occurred: {e}")
