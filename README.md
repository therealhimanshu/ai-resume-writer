# AI Resume Tailor

A Streamlit app that tailors a master resume to a target job description using Google Gemini.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install streamlit requests beautifulsoup4 pypdf google-generativeai
   ```
3. Set `GEMINI_API_KEY` in your environment or Streamlit secrets.
4. Run:
   ```bash
   streamlit run app.py
   ```

## Notes

- Upload your resume as a PDF.
- Provide the job description as a URL or pasted text.
- The app generates a Markdown-tailored resume based on the target JD.
