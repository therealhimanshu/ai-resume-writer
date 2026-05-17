import streamlit as st
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(
    page_title="AI Resume Tailor",
    page_icon="💼",
    layout="centered"
)

# Initialize Gemini Client using Streamlit Secrets
# It will look for GEMINI_API_KEY in your environment/secrets
try:
    client = genai.Client()
except Exception as e:
    st.error("API Key missing. Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

def extract_text_from_pdf(uploaded_file) -> str:
    """Extracts text from an uploaded PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def extract_jd_from_url(url: str) -> str:
    """Scrapes raw text from a job posting URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Strip script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        st.error(f"Could not automatically fetch URL: {e}. Please copy-paste the JD text instead.")
        return ""

def tailor_resume(master_resume: str, job_description: str) -> str:
    """Calls Gemini 2.5 Flash to optimize the resume text."""
    prompt = f"""
    You are an expert technical recruiter and elite resume writer. Your task is to tailor a candidate's Master Resume to perfectly align with a target Job Description (JD). 

    CRITICAL RESTRAINT RULES:
    1. DO NOT invent, hallucinate, or fabricate any experience, specific metrics, tools, or roles. Work strictly with the facts provided in the Master Resume.
    2. Optimize for ATS (Applicant Tracking Systems) by naturally weaving in exact keywords, hard skills, and methodologies found in the JD.
    3. Rewrite impact points using the X-Y-Z formula (Accomplished [X] as measured by [Y], by doing [Z]) where applicable, emphasizing relevant business or data impact.
    4. Keep the output professional, crisp, and clean.

    ---
    TARGET JOB DESCRIPTION:
    {job_description}

    ---
    CANDIDATE'S MASTER RESUME:
    {master_resume}
    ---

    Provide the final tailored resume in clean Markdown format. 
    At the absolute top, include a short 3-bullet block titled "🎯 ATS Alignment Summary" explaining exactly what keywords were matched and what strategic modifications were made.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,  # Focused and analytical
        )
    )
    return response.text

# --- UI Layout ---
st.title("💼 Personal AI Resume Tailor")
st.caption("Instantly align your master resume with any job role using Gemini 2.5 Flash.")

st.markdown("---")

# Section 1: Master Resume Input
st.subheader("1. Upload Your Master Resume")
uploaded_resume = st.file_uploader("Upload PDF Version", type=["pdf"])

# Section 2: Job Description Input
st.subheader("2. Target Job Details")
jd_source_type = st.radio("Provide Job Description via:", ["Paste URL Link", "Paste Raw Text"])

jd_text = ""
if jd_source_type == "Paste URL Link":
    jd_url = st.text_input("Job Posting URL (LinkedIn, Indeed, Company Site etc.)")
    if jd_url:
        with st.spinner("Scraping job description..."):
            jd_text = extract_jd_from_url(jd_url)
else:
    jd_text = st.text_area("Paste the text of the job description here", height=200)

st.markdown("---")

# Section 3: Execution
if st.button("🚀 Tailor My Resume", type="primary"):
    if not uploaded_resume:
        st.warning("Please upload your master resume PDF first.")
    elif not jd_text.strip():
        st.warning("Please provide a valid job description or link.")
    else:
        with st.spinner("Gemini is analyzing the JD and reframing your achievements..."):
            # Process PDF
            resume_content = extract_text_from_pdf(uploaded_resume)
            
            if resume_content:
                # Call AI
                final_tailored_resume = tailor_resume(resume_content, jd_text)
                
                # Show Output
                st.success("🎉 Done! Review your tailored resume below:")
                
                # Download Button
                st.download_button(
                    label="📥 Download Tailored Resume (.md)",
                    data=final_tailored_resume,
                    file_name="tailored_resume.md",
                    mime="text/markdown"
                )
                
                # Display on Screen
                st.markdown(final_tailored_resume)