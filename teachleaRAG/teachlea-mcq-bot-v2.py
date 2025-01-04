import openai
import streamlit as st
# from dotenv import load_dotenv
# import os

# Load environment variables
# load_dotenv()

# Set your OpenAI API key
openai.api_key = st.secrets["OPEN_AI_KEY"]

# Streamlit UI
st.title("Interactive MCQ Generator with Validation")

st.sidebar.header("Instructions")
st.sidebar.write("""
1. Enter a topic and the number of MCQs to generate.
2. Select your answers.
3. Submit your answers to validate them.
""")

# Input: Topic and number of questions
topic = st.text_input("Enter the topic for MCQs:", "Python Programming")
num_questions = st.number_input("Number of MCQs to generate:", min_value=1, max_value=20, value=5)

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

            # Parse response
            generated_mcqs = response['choices'][0]['message']['content'].strip().split("\n\n")
            st.session_state.mcqs = []
            for mcq in generated_mcqs:
                lines = mcq.split("\n")
                if len(lines) >= 6:  # Ensure valid structure (1 question + 4 options + 1 answer line)
                    question = lines[0].strip()
                    options = [line.strip() for line in lines[1:5]]
                    correct_answer = lines[5].split(":")[-1].strip()
                    st.session_state.mcqs.append({
                        "question": question,
                        "options": options,
                        "correct_answer": correct_answer,
                        "user_answer": None
                    })
            if not st.session_state.mcqs:
                st.error("Failed to parse MCQs. Please try again.")
            else:
                st.success("MCQs Generated Successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Display MCQs and collect user answers
if "mcqs" in st.session_state:
    st.header("Answer the MCQs")
    for idx, mcq in enumerate(st.session_state.mcqs):
        st.subheader(mcq["question"])
        mcq["user_answer"] = st.radio(f"Select your answer for Q{idx + 1}:", mcq["options"], key=f"q{idx}")

    if st.button("Submit Answers"):
        with st.spinner("Validating your answers..."):
            try:
                st.header("Results")
                score = 0
                for idx, mcq in enumerate(st.session_state.mcqs):
                    # Ensure that user_answer is selected
                    if mcq["user_answer"]:
                        correct = mcq["correct_answer"]
                        user_answer = mcq["user_answer"]

                        # Match the correct answer (which is given as 'a', 'b', 'c', or 'd') with the option list
                        correct_option = mcq["options"][ord(correct.lower()) - ord('a')]

                        # Validate directly by checking if the user's answer matches the correct option
                        if user_answer == correct_option:
                            st.success(f"**Q{idx + 1}:** Correct!")
                            score += 1
                        else:
                            # Show the correct answer as text (e.g., Option a: correct option)
                            st.error(f"**Q{idx + 1}:** Incorrect. Correct answer: {correct_option}")

                    else:
                        st.warning(f"**Q{idx + 1}:** No answer selected.")

                st.write(f"**Your Total Score: {score}/{len(st.session_state.mcqs)}**")

            except Exception as e:
                st.error(f"An error occurred during validation: {e}")
