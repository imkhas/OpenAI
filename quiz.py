import streamlit as st
from openai import OpenAI
import os
my_secret = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=my_secret)
def generate_question(topic):
    system_prompt = """
    You are an expert quiz creator. Generate a multiple-choice question on the given topic.
    The response should be in the following format:
    Question: [The question]
    A. [Option A]
    B. [Option B]
    C. [Option C]
    D. [Option D]
    Correct Answer: [The correct option letter]
    Explanation: [A brief explanation of why this is the correct answer]
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate a question about {topic}"}
        ],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content
def evaluate_answer(user_answer, correct_answer, explanation):
    if user_answer.upper() == correct_answer.upper():
        st.success("Correct!")
    else:
        st.error(f"Incorrect. The correct answer is {correct_answer}.")
    st.write(f"Explanation: {explanation}")
st.title("Quiz Generator App")
st.divider()
topic = st.text_input("Enter a topic for the quiz:")
if 'question_generated' not in st.session_state:
    st.session_state.question_generated = False
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False
if st.button("Generate Question"):
    with st.spinner("Generating question..."):
        question_data = generate_question(topic)
        # Parse the question data
        lines = question_data.split('\n')
        st.session_state.question = lines[0].replace("Question: ", "")
        st.session_state.options = lines[1:5]
        st.session_state.correct_answer = lines[5].replace("Correct Answer: ", "")
        st.session_state.explanation = lines[6].replace("Explanation: ", "")
        st.session_state.question_generated = True
        st.session_state.answer_submitted = False
if st.session_state.question_generated:
    # Display the question and options
    st.write(st.session_state.question)
    for option in st.session_state.options:
        st.write(option)
    # Get user's answer
    user_answer = st.radio("Select your answer:", ["A", "B", "C", "D"])
    if st.button("Submit Answer"):
        st.session_state.answer_submitted = True
        evaluate_answer(user_answer, st.session_state.correct_answer, st.session_state.explanation)
st.divider()
st.write("")

