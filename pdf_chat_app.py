import streamlit as st
import pdfplumber
from openai import OpenAI

# --- Load & validate OpenAI API key from Streamlit secrets ---
api_key = st.secrets.get("OPENAI_API_KEY")
# Debug: confirm whether the key was loaded
st.write("🔍 Loaded key?", bool(api_key))
if not api_key:
    st.error(
        "🔑 No OpenAI key found! Add OPENAI_API_KEY in Manage App → Settings → Secrets."
    )
    st.stop()

# Initialize OpenAI client with the loaded key
client = OpenAI(api_key=api_key)

# --- Function to extract text from the uploaded PDF ---
def extract_pdf_text(uploaded_file):
    """
    Extracts and concatenates text from all pages of a PDF file.
    """
    with pdfplumber.open(uploaded_file) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)

# --- Function to ask a question to the PDF content via OpenAI ---
def ask_pdf_question(text, question):
    """
    Sends the PDF text and user's question to OpenAI and returns the response.
    """
    # Build prompt combining PDF content and user question
    prompt = (
        "Answer the question using only the content from the PDF below.\n\n"
        f"PDF Content:\n{text}\n\n"
        f"Question: {question}"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that only uses the provided PDF text."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.2,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

# --- Streamlit App UI ---
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
        # Display the answer
        st.markdown(f"**Answer:**\n\n{answer}")
