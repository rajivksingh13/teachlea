import openai
import streamlit as st
import pyttsx3
import speech_recognition as sr
import tempfile

# Set OpenAI API Key
openai.api_key = st.secrets["OPEN_AI_KEY"]

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Adjust speaking rate

# Streamlit UI
st.title("Real-Time Voice Chatbot")
st.markdown("### Speak to the bot, and it will respond in real-time!")


# Function to convert text to speech and save it as a temporary audio file
def text_to_speech(text):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    engine.save_to_file(text, temp_file.name)
    engine.runAndWait()
    return temp_file.name


# Function to recognize speech
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            st.write("Listening... Speak now.")
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            return None  # No speech detected
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."
        except Exception as e:
            return f"Error: {e}"


# Chatbot function
def generate_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An error occurred: {e}"


# Initialize session states
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "stop_listening" not in st.session_state:
    st.session_state["stop_listening"] = False

# Checkbox to control listening
stop_listening_checkbox = st.checkbox("Stop Listening", key="stop_listening_checkbox")
st.session_state["stop_listening"] = stop_listening_checkbox

if not st.session_state["stop_listening"]:  # Only run if the checkbox is unchecked
    st.markdown("### Real-Time Conversation")
    st.info("The chatbot is listening. Speak into your microphone.")

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while not st.session_state["stop_listening"]:  # Recheck the session state
            user_query = speech_to_text()
            if user_query:
                st.markdown(f"**You said:** {user_query}")
                bot_response = generate_response(user_query)
                if bot_response:
                    st.markdown(f"**Chatbot:** {bot_response}")

                    # Generate voice response
                    audio_file = text_to_speech(bot_response)
                    st.audio(audio_file, format="audio/wav", start_time=0)

                    # Append to chat history
                    st.session_state["chat_history"].append({"user": user_query, "bot": bot_response})
            # Break the loop if the checkbox is toggled
            if st.session_state["stop_listening"]:
                break
