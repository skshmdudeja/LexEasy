# ⚖️ LexEasy — Legal Document Simplifier

An AI-powered tool that simplifies Indian legal documents into plain Hinglish.

## Problem
Common Indians blindly sign legal documents like rent agreements, offer letters, and NDAs because legal language is complex and lawyers are expensive.

## Solution
LexEasy analyzes any legal document and provides:
- Simple Hinglish summary
- Key clauses explained in plain language
- Red flag detection
- Risk Score (Low / Medium / High)
- Practical recommendations before signing

## Features
- Text paste support
- Photo upload with OCR
- PDF upload support
- 8 document types supported
- Risk scoring system
- Hinglish output for Indian users

## Tech Stack
- Python
- Streamlit
- Groq API (LLaMA 3.3)
- Pytesseract (OCR)
- PyMuPDF (PDF parsing)

## How to Run
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Groq API key in `.env` file
4. Run: `streamlit run app.py`