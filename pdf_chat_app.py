import streamlit as st
import pdfplumber
import openai
import os

# Use environment variable for security
openai.api_key = os.getenv("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")

def extract_pdf_text(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def ask_pdf_question(text, question):
    prompt = f"""
Answer the question using only the content from the PDF below.

PDF Content:
\"\"\"
{text}
\"\"\"

Question: {question}
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that only uses the provided PDF text."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=600
    )
    return response["choices"][0]["message"]["content"]

# --- Streamlit UI ---
st.title("📄 Chat with your PDF")
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    with st.spinner("Reading PDF..."):
        pdf_text = extract_pdf_text(uploaded_file)

    st.success("✅ PDF loaded. Ask a question!")

    question = st.text_input("What do you want to know?")
    if question:
        with st.spinner("Thinking..."):
            answer = ask_pdf_question(pdf_text, question)
            st.markdown(f"**Answer:**\n{answer}")
