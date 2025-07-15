import streamlit as st
import pdfplumber
import os
from openai import OpenAI

# —————————————————————
# 1) API-KEY HANDLING
# —————————————————————

# First try the environment (secrets)
api_key = os.getenv("OPENAI_API_KEY")

# If not found, prompt the user with a password field
if not api_key:
    st.warning("🔑 Enter your OpenAI API Key below to get started.")
    api_key = st.text_input("OpenAI API Key", type="password")

# If we still don’t have a key, stop here
if not api_key:
    st.stop()

# Initialize the client
client = OpenAI(api_key=api_key)

# —————————————————————
# 2) PDF TEXT EXTRACTION
# —————————————————————

def extract_pdf_text(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return "\n".join(
            page.extract_text() or "" 
            for page in pdf.pages
        ).strip()

# —————————————————————
# 3) ASKING GPT
# —————————————————————

def ask_pdf_question(text, question):
    prompt = f"""
Answer the question using only the content from the PDF below.

PDF Content:
\"\"\"
{text}
\"\"\"

Question: {question}
"""
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that only uses the provided PDF text."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.2,
        max_tokens=600
    )
    return resp.choices[0].message.content

# —————————————————————
# 4) STREAMLIT UI
# —————————————————————

st.title("📄 Chat with your PDF")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    with st.spinner("Reading PDF…"):
        pdf_text = extract_pdf_text(uploaded_file)
    st.success("✅ PDF loaded! Ask away below.")

    question = st.text_input("What do you want to know about the document?")
    if question:
        with st.spinner("Thinking…"):
            answer = ask_pdf_question(pdf_text, question)
        st.markdown(f"**Answer:**  \n{answer}")

