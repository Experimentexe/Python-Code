import streamlit as st
import pandas as pd
import plotly.express as px
from pypdf import PdfReader
from openai import OpenAI
import requests
import trafilatura
import json
import os

st.set_page_config(page_title="Resume Review",page_icon="	:clipboard:",layout="wide")
client = OpenAI(api_key="Your Key Here")

def load_resume(file):
        try:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                text= text+page_text+"\n"
            st.write("File Upload Has Been Successful")
            return text
        except Exception as e:
               st.error(f"Error processing Resume: {str(e)}")
               return None
        
def extract_json(text):
    return json.loads(text)


def main():
    st.title("📄 Resume Review AI")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    jobPostingURL = st.text_area("Paste Job Description")

    if st.button("Analyze Resume"):

        # -----------------------
        # VALIDATION
        # -----------------------
        if not uploaded_file:
            st.error("Please upload a resume PDF.")
            return

        if not jobPostingURL.strip():
            st.error("Please paste a job description.")
            return

        # -----------------------
        # EXTRACT RESUME TEXT
        # -----------------------
        resume_text = load_resume(uploaded_file)

        if not resume_text:
            st.error("Failed to extract resume text.")
            return

        # -----------------------
        # BUILD PROMPT
        # -----------------------
        prompt = f"""
You are a Senior Technical Recruiter and ATS Resume Reviewer.

IMPORTANT RULES:
- Do NOT invent or assume experience
- Be strict, honest, and critical
- Evaluate like a real hiring decision

JOB DESCRIPTION:
{jobPostingURL}

RESUME:
{resume_text}

Return ONLY valid JSON:

{{
  "ats_score": "",
  "verdict": "",
  "strengths": [],
  "weaknesses": [],
  "keywords_missing": [],
  "structure_fixes": [],
  "line_improvements": [],
  "final_strategy": ""
}}
"""

        # -----------------------
        # CALL GPT (SAFE)
        # -----------------------
        try:
            response_GPT = client.responses.create(
                model="gpt-5",
                input=prompt
            )

            raw_output = response_GPT.output_text

        except Exception as e:
            st.error(f"GPT API Error: {str(e)}")
            return

        # -----------------------
        # PARSE JSON SAFELY
        # -----------------------
        try:
            data = extract_json(raw_output)

        except Exception:
            st.error("Model did not return valid JSON. Raw output below:")
            st.text(raw_output)
            return

        # -----------------------
        # DISPLAY RESULTS
        # -----------------------
        st.subheader("ATS Score")
        st.write(data.get("ats_score"))

        st.subheader("Verdict")
        st.write(data.get("verdict"))

        st.subheader("Strengths")
        st.write(data.get("strengths"))

        st.subheader("Weaknesses")
        st.write(data.get("weaknesses"))

        st.subheader("Missing Keywords")
        st.write(data.get("keywords_missing"))

        st.subheader("Structure Fixes")
        st.write(data.get("structure_fixes"))

        st.subheader("Line Improvements")
        st.write(data.get("line_improvements"))

        st.subheader("Final Strategy")
        st.write(data.get("final_strategy"))
main()
