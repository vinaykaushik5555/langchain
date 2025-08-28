from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

model = ChatOpenAI(temperature=0.1)
st.set_page_config(page_title="Prompt Summarizer", page_icon="📝", layout="centered")

st.title("Prompt Summarizer")

prompt = st.text_input("Enter your prompt:")

if st.button("Submit") and prompt:
    answer = model.invoke(prompt).content
    st.text_area("Answer", value=answer, height=500)