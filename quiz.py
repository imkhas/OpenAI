import streamlit as st
from openai import OpenAI
import os
from PIL import Image
import io
import base64

my_secret = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=my_secret)

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def generate_text_questions(topic, num_questions):
    system_prompt = f"""
    You are an expert quiz creator. Generate {num_questions} multiple-choice questions on the given topic.
    Each question should be in the following format:
    Question: [The question]
    A. [Option A]
    B. [Option B]
    C. [Option C]
    D. [Option D]
    Correct Answer: [The correct option letter]
    Explanation: [A brief explanation of why this is the correct answer]

    Separate each question with a newline.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate questions about {topic}"}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    return response.choices[0].message.content.split('\n\n')

def generate_image_questions(image, num_questions):
    base64_image = encode_image(image)

    system_prompt = f"""
    You are an expert quiz creator. Analyze the given image and generate {num_questions} multiple-choice questions based on the content of the image.
    Each question should be in the following format:
    Question: [The question]
    A. [Option A]
    B. [Option B]
    C. [Option C]
    D. [Option D]
    Correct Answer: [The correct option letter]
    Explanation: [A brief explanation of why this is the correct answer]

    Separate each question with a newline.
    """

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": "Generate questions based on this image."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        max_tokens=2000
    )
    return response.choices[0].message.content.split('\n\n')

def parse_question(question_data):
    lines = question_data.split('\n')
    return {
        'question': lines[0].replace("Question: ", ""),
        'options': lines[1:5],
        'correct_answer': lines[5].replace("Correct Answer: ", ""),
        'explanation': lines[6].replace("Explanation: ", "")
    }

st.title("Versatile Quiz Generator")
st.divider()

quiz_type = st.radio("Choose quiz type:", ["Text-based", "Image-based"])

if quiz_type == "Text-based":
    topic = st.text_input("Enter a topic for the quiz:")
else:
    uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])

num_questions = st.number_input("How many questions do you want? (Max 10)", min_value=1, max_value=10, value=3)

if 'questions' not in st.session_state:
    st.session_state.questions = []

if 'current_question' not in st.session_state:
    st.session_state.current_question = 0

if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}

if st.button("Generate Quiz"):
    if quiz_type == "Text-based" and topic:
        with st.spinner(f"Generating {num_questions} questions about {topic}..."):
            questions_data = generate_text_questions(topic, num_questions)
            st.session_state.questions = [parse_question(q) for q in questions_data]
    elif quiz_type == "Image-based" and uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        with st.spinner(f"Generating {num_questions} questions based on the image..."):
            questions_data = generate_image_questions(uploaded_file, num_questions)
            st.session_state.questions = [parse_question(q) for q in questions_data]
    else:
        st.error("Please provide a topic or upload an image before generating the quiz.")

    if st.session_state.questions:
        st.session_state.current_question = 0
        st.session_state.user_answers = {}

if st.session_state.questions:
    current_q = st.session_state.questions[st.session_state.current_question]

    st.write(f"Question {st.session_state.current_question + 1} of {len(st.session_state.questions)}")
    st.write(current_q['question'])
    for option in current_q['options']:
        st.write(option)

    user_answer = st.radio("Select your answer:", ["A", "B", "C", "D"], 
                           key=f"q{st.session_state.current_question}",
                           index=["A", "B", "C", "D"].index(st.session_state.user_answers.get(st.session_state.current_question, "A")))

    st.session_state.user_answers[st.session_state.current_question] = user_answer

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Back", disabled=st.session_state.current_question == 0):
            st.session_state.current_question -= 1
            st.experimental_rerun()

    with col2:
        if st.button("Next", disabled=st.session_state.current_question == len(st.session_state.questions) - 1):
            st.session_state.current_question += 1
            st.experimental_rerun()

    if len(st.session_state.user_answers) == len(st.session_state.questions):
        if st.button("Submit Answers"):
            score = 0
            for i, q in enumerate(st.session_state.questions):
                user_ans = st.session_state.user_answers.get(i)
                is_correct = user_ans.upper() == q['correct_answer'].upper()
                if is_correct:
                    score += 1
                st.write(f"Question {i+1}: {'Correct' if is_correct else 'Incorrect'}")
                st.write(f"Your answer: {user_ans}")
                st.write(f"Correct answer: {q['correct_answer']}")
                st.write(f"Explanation: {q['explanation']}")
                st.write("---")

            st.success(f"Quiz completed! Your score: {score}/{len(st.session_state.questions)}")

st.divider()
st.write("Note: This app uses OpenAI's API to generate questions. The content is AI-generated and may not always be perfectly accurate.")