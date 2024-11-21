import pandas as pd
import streamlit as st
import base64
import os
import io
from dotenv import load_dotenv
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize session state variables if they don't exist
if "response" not in st.session_state:
    st.session_state.response = None
if "missing_keywords" not in st.session_state:
    st.session_state.missing_keywords = []

# Function to get a Gemini response
def get_gemini_response(input_text, pdf_content, prompt, model_name="gemini-1.5-flash"):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([input_text, pdf_content[0], prompt])
        return response.text
    except Exception as e:
        return f"Error: {e}"

# Function to process uploaded PDF and convert to base64-encoded image
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to recommend YouTube videos for resume improvement
def recommend_videos():
    st.markdown("### 📚 Recommendations to Improve Your Resume")
    st.write("Here are some curated YouTube videos to help you create a stronger, ATS-friendly resume:")
    videos = [
        {
            "title": "How to Create a Perfect Resume (Step-by-Step)",
            "url": "https://www.youtube.com/watch?v=ZQYNu7-9OC8"
        },
        {
            "title": "Top 5 Resume Tips | Improve Your Resume Quickly",
            "url": "https://www.youtube.com/watch?v=rQwanxQmFnc"
        },
        {
            "title": "ATS-Friendly Resume Formatting Tips",
            "url": "https://www.youtube.com/watch?v=KkMdAb-zpEE"
        },
        {
            "title": "How to Use Keywords in Your Resume for ATS",
            "url": "https://www.youtube.com/watch?v=3gSY7ORvJBI"
        },
    ]
    for video in videos:
        st.markdown(f"- **[{video['title']}]({video['url']})**")

# Function to export results to CSV
def export_results_to_csv(report_data):
    # Create a DataFrame from the report data
    df = pd.DataFrame([report_data])
    # Save the DataFrame as a CSV in memory
    csv_data = df.to_csv(index=False).encode('utf-8')
    return csv_data

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert", page_icon="📄", layout="wide")
st.markdown("<style>h1{color: #4CAF50;}</style>", unsafe_allow_html=True)

# Header Section
st.markdown("<h1 style='text-align: center;'>ATS Resume Expert</h1>", unsafe_allow_html=True)
st.write("---")

# Sidebar
st.sidebar.header("🔍 Navigation")
st.sidebar.markdown("""
Use the buttons below to:
- Upload your resume.
- Analyze your resume.
- Get resume improvement tips.
""")

# Input fields
st.markdown("### 📋 Job Description")
input_text = st.text_area("Enter the job description here:", key="input", height=150)

st.markdown("### 📄 Upload Resume")
uploaded_file = st.file_uploader("Upload your resume (PDF format only):", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ Resume uploaded successfully!")

# Buttons for functionalities
st.markdown("### 💡 Choose Your Action")
col1, col2, col3 = st.columns(3)
with col1:
    submit1 = st.button("Analyze Resume")
with col2:
    submit3 = st.button("Check Percentage Match")
with col3:
    submit_recommend = st.button("Get Recommendations")

# Prompts for analysis
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. Provide the percentage match, missing keywords, 
and final thoughts. Format the output as follows:
1. Percentage match.
2. Missing keywords.
3. Final thoughts.
"""

# Functionality for "Analyze Resume"
if submit1:
    if uploaded_file is not None:
        try:
            pdf_content = input_pdf_setup(uploaded_file)
            st.session_state.response = get_gemini_response(input_text, pdf_content, input_prompt1)
            st.markdown("### 📝 Analysis Result")
            st.write(st.session_state.response)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("⚠️ Please upload your resume first.")

# Functionality for "Check Percentage Match"
elif submit3:
    if uploaded_file is not None:
        try:
            pdf_content = input_pdf_setup(uploaded_file)
            st.session_state.response = get_gemini_response(input_text, pdf_content, input_prompt3)
            st.markdown("### 📊 Percentage Match Result")
            st.write(st.session_state.response)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("⚠️ Please upload your resume first.")

# Functionality for "Get Recommendations"
elif submit_recommend:
    if uploaded_file is not None:
        recommend_videos()
    else:
        st.warning("⚠️ Please upload your resume to get recommendations.")


# Buttons to download the report as CSV or PDF
from fpdf import FPDF
import io

# Function to export results to PDF using DejaVu font
def export_results_to_pdf(report_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Add the DejaVu font (ensure the correct path to the font file)
    pdf.add_font("DejaVu", "", os.path.join("fonts", "DejaVuSans.ttf"), uni=True)
    pdf.set_font("DejaVu", size=12)

    # Add header
    pdf.cell(200, 10, "Resume Analysis Report", ln=True, align="C")
    pdf.ln(10)

    # Add Job Description
    pdf.cell(200, 10, "Job Description:", ln=True)
    pdf.multi_cell(0, 10, report_data['Job Description'])
    pdf.ln(10)

    # Add Resume Analysis
    pdf.cell(200, 10, "Resume Analysis:", ln=True)
    pdf.multi_cell(0, 10, report_data['Resume Analysis'])
    pdf.ln(10)

    
    # Output the PDF to a byte stream
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)  # Move to the start of the stream

    return pdf_output


# Button to download the report as PDF
st.markdown("### 📥 Download PDF Report")
if st.session_state.response:  # Ensure analysis has been performed
    report_data = {
        "Job Description": input_text,
        "Resume Analysis": st.session_state.response,
        "Percentage Match": st.session_state.percentage_match if "percentage_match" in st.session_state else "N/A",
        "Missing Keywords": st.session_state.missing_keywords if st.session_state.missing_keywords else [],
    }
    # Export the results to PDF
    pdf_data = export_results_to_pdf(report_data)
    st.download_button(
        label="Download PDF Report",
        data=pdf_data,
        file_name="resume_analysis_report.pdf",
        mime="application/pdf"
    )
else:
    st.warning("⚠️ Please analyze the resume before downloading the report.")
