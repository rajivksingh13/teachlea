import openai
import streamlit as st
# from dotenv import load_dotenv
# import os

# Load environment variables
# load_dotenv()

# Set your OpenAI API key
# openai.api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
# Set your OpenAI API key
openai.api_key = st.secrets["OPEN_AI_KEY"]
# Streamlit UI
st.title("Teachlea MCQ Generator with OpenAI")

st.sidebar.header("Instructions")
st.sidebar.write("""
1. Enter a topic or concept.
2. Set the number of MCQs to generate.
3. Click 'Generate MCQs'.
""")

# Input: Topic and number of questions
topic = st.text_input("Enter the topic for MCQs:", "Python Programming")
num_questions = st.number_input("Number of MCQs to generate:", min_value=1, max_value=20, value=5)

# Button to generate MCQs
if st.button("Generate MCQs"):
    with st.spinner("Generating MCQs..."):
        try:
            # OpenAI API call to generate MCQs
            prompt = f"""
Generate {num_questions} multiple-choice questions (MCQs) on the topic "{topic}".
Each question should include 4 options and clearly indicate the correct answer. Format the response as:
1. Question text
    a) Option 1
    b) Option 2
    c) Option 3
    d) Option 4
    Correct Answer: (letter corresponding to the correct answer)
"""
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # Display the generated MCQs
            st.success("MCQs Generated Successfully!")
            st.markdown(response['choices'][0]['message']['content'].strip())
        except Exception as e:
            st.error(f"An error occurred: {e}")
