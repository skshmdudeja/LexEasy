import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from PIL import Image
import pytesseract
import fitz
import shutil

# ==========================================
# CROSS-PLATFORM TESSERACT CONFIGURATION
# ==========================================
# 1. First, check if running on Streamlit Cloud (Linux)
linux_tesseract_path = '/usr/bin/tesseract'
dynamic_path = shutil.which("tesseract")

if os.path.exists(linux_tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = linux_tesseract_path
elif dynamic_path:
    pytesseract.pytesseract.tesseract_cmd = dynamic_path
else:
    # 2. Fallback to your local Windows path if running locally
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Session State
if "analysis" not in st.session_state:
    st.session_state.analysis = ""
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

# Sidebar
st.sidebar.title("⚖️ LexEasy")
st.sidebar.markdown("---")
doc_type = st.sidebar.selectbox(
    "Select Document Type",
    [
        "Rent Agreement",
        "Offer Letter",
        "NDA",
        "Property Registry",
        "Legal Notice",
        "Court Summons",
        "Service Agreement",
        "Other"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("Apna document paste karo ya photo/PDF upload karo aur Analyze dabao.")

# Main UI
st.title("⚖️ LexEasy — Legal Document Simplifier")
st.subheader("Legal documents ko simple Hinglish mein samjho")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    input_method = st.radio(
        "Input Method Chuno",
        ["Text Paste Karo", "Photo Upload Karo", "PDF Upload Karo"]
    )

    if input_method == "Text Paste Karo":
        st.session_state.extracted_text = ""
        document = st.text_area(
            "Paste your document here",
            height=300,
            placeholder="Copy and paste your legal document text here..."
        )

    elif input_method == "Photo Upload Karo":
        uploaded_file = st.file_uploader(
            "Document ki photo upload karo",
            type=["jpg", "jpeg", "png"]
        )
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Document", use_container_width=True)
            with st.spinner("Photo se text nikal raha hai..."):
                try:
                    st.session_state.extracted_text = pytesseract.image_to_string(image)
                except Exception as e:
                    st.error(f"OCR Error: {e}")
                    st.info("Make sure you have added packages.txt to your GitHub repo and redeployed.")
            
            if st.session_state.extracted_text.strip():
                st.success("Text extract ho gaya!")
            else:
                st.error("Photo se text nahi nikal paya — clearer photo try karo.")
        document = st.session_state.extracted_text

    elif input_method == "PDF Upload Karo":
        uploaded_pdf = st.file_uploader(
            "PDF upload karo",
            type=["pdf"]
        )
        if uploaded_pdf is not None:
            with st.spinner("PDF se text nikal raha hai..."):
                pdf_bytes = uploaded_pdf.read()
                pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
                extracted = ""
                for page in pdf_document:
                    extracted += page.get_text()
                st.session_state.extracted_text = extracted
            if st.session_state.extracted_text.strip():
                st.success(f"PDF se text extract ho gaya — {pdf_document.page_count} pages padhe!")
            else:
                st.error("PDF se text nahi nikal paya — try another PDF.")
        document = st.session_state.extracted_text

with col2:
    st.markdown("### How to use")
    st.markdown("1. Sidebar se document type chuno")
    st.markdown("2. Text paste karo ya photo/PDF upload karo")
    st.markdown("3. Analyze Document dabao")
    st.markdown("4. Simple Hinglish mein analysis pao")
    st.markdown("---")
    st.warning("LexEasy sirf informational tool hai. Legal advice ke liye lawyer se milo.")

st.markdown("---")

# Doc Context
doc_context = {
    "Rent Agreement": "Isme landlord aur tenant ke beech property kiraye ka agreement hota hai. Dhyan rakho — rent, security deposit, notice period, maintenance, aur agreement khatam karne ke clauses pe.",
    "Offer Letter": "Isme company employee ko job offer karti hai. Dhyan rakho — salary, bond period, joining date, agreement khatam karne ka clause, aur hidden conditions pe.",
    "NDA": "Isme ek party doosri party ko secret information share karti hai. Dhyan rakho — kya share ho sakta hai, kya nahi, kitne time tak, aur penalty kya hai.",
    "Property Registry": "Isme property ka ownership transfer hota hai. Dhyan rakho — property details, stamp duty, aur buyer seller ke rights pe.",
    "Legal Notice": "Yeh ek formal legal warning hai. Dhyan rakho — kya demand ki gayi hai, deadline kya hai, aur kya action lena chahiye.",
    "Court Summons": "Yeh court ka bulawa hai. Dhyan rakho — court ka naam, date, time, reason, aur kya karna chahiye.",
    "Service Agreement": "Isme ek party doosri party ko service provide karti hai. Dhyan rakho — payment terms, delivery, penalties, aur agreement khatam karne pe.",
    "Other": "Yeh ek legal document hai. Sabse important clauses, rights, obligations, aur risks pe dhyan rakho."
}

# Analyze Button
if st.button("🔍 Analyze Document", use_container_width=True):
    if document and document.strip():
        with st.spinner("Document analyze ho raha hai..."):

            system_prompt = f"""
Tu ek helpful legal document assistant hai jo common Indians ki madad karta hai.
User ne ek {doc_type} paste kiya hai.

{doc_context[doc_type]}

Sabse pehle EXACTLY yeh line likho:
RISK_SCORE: LOW ya RISK_SCORE: MEDIUM ya RISK_SCORE: HIGH

Phir EXACTLY is format mein jawab de:

## Document Summary
3-4 simple lines mein batao — yeh agreement kiske beech hai, kya hai, kitne time ke liye hai.

## Key Clauses
Har important point ko bilkul simple bhasha mein likho.
Aise likho jaise kisi dost ko samjha rahe ho.
Koi bhi hard English legal word mat use karo.
Bullet points mein likho.

## Red Flags
Koi bhi risky ya unfair cheez hai toh clearly batao — user ko kya nuksan ho sakta hai.
Agar koi nahi hai toh likho: "Koi bada risk nahi mila."

## Recommendations
2-3 practical tips — sign karne se pehle kya karna chahiye.
Bilkul simple aur actionable rakho.

IMPORTANT RULES:
- Koi bhi hard English legal word mat use karo
- Aise likho jaise ek dost samjha raha ho
- Forfeit ki jagah "paisa doob jaayega" likho
- Terminate ki jagah "agreement khatam kar dena" likho
- Utilities ki jagah "bijli paani ka bill" likho
"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": document}
                ]
            )

            st.session_state.analysis = response.choices[0].message.content

    else:
        st.warning("Pehle document paste karo ya photo/PDF upload karo.")

# Output
if st.session_state.analysis:
    st.markdown("---")

    # Risk Score parse karo
    response_text = st.session_state.analysis
    risk_score = "MEDIUM"

    if "RISK_SCORE: LOW" in response_text:
        risk_score = "LOW"
    elif "RISK_SCORE: HIGH" in response_text:
        risk_score = "HIGH"
    else:
        risk_score = "MEDIUM"

    # Clean text
    clean_analysis = response_text.replace(f"RISK_SCORE: {risk_score}", "").strip()

    # Risk Score display
    if risk_score == "LOW":
        st.success("🟢 Risk Level: LOW — Yeh document relatively safe lag raha hai.")
    elif risk_score == "MEDIUM":
        st.warning("🟡 Risk Level: MEDIUM — Kuch clauses dhyan se padho.")
    elif risk_score == "HIGH":
        st.error("🔴 Risk Level: HIGH — Sign karne se pehle lawyer se milo.")

    # Analysis display
    with st.expander("📄 Full Analysis Dekho", expanded=True):
        st.markdown(clean_analysis)

    st.markdown("---")
    st.caption("⚠️ LexEasy sirf informational tool hai. Kisi bhi legal decision ke liye qualified lawyer se consult karo.")
