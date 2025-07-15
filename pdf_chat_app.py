import streamlit as st
import pdfplumber
from openai import OpenAI
import os

# --- Set up OpenAI client using new SDK ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Function to extract text from PDF ---
def extract_pdf_text(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return "\n".join(
            page.extract_text() for page in pdf.pages if page.extract_text()
        )

# --- Function to ask question via OpenAI ---
def ask_pdf_question(text, question):
    prompt = f"""
Answer the question using only the content from the PDF below.

PDF Content:
\"\"\"
{text}
\"\"\"

Question: {question}
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that only uses the provided PDF text."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=600
    )
    return response.choices[0].message.content

# --- Streamlit Interface ---
st.title("📄 Chat with your PDF")
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    with st.spinner("Reading PDF..."):
        pdf_text = extract_pdf_text(uploaded_file)
    st.success("✅ PDF loaded. Ask your question!")

    question = st.text_input("What do you want to know?")
    if question:
        with st.spinner("Thinking..."):
            answer = ask_pdf_question(pdf_text, question)
            st.markdown(f"**Answer:**\n{answer}")
