import streamlit as st
import openai
from datetime import datetime
from jinja2 import Template
import base64
import os
from weasyprint import HTML
from pathlib import Path
HTML("resume.html").write_pdf("resume.pdf")

with st.sidebar:
    st.session_state["api_key"] = st.text_input("place your api key here")

if st.session_state["api_key"]:
    client = openai.OpenAI(api_key=st.session_state["api_key"])
else:
    st.error("No API key provided.")





st.set_page_config(layout="wide")
st.title("📄 Smart Resume Builder with PDF & Photo")

# Upload Profile Image
photo = st.file_uploader("Upload a profile photo (JPG or PNG)", type=["jpg", "jpeg", "png"])

# Sidebar Inputs (Left 1/3)
with st.sidebar:
    st.header("🧠 Skills & 🌐 Languages")
    skills = st.text_area("Skills (comma-separated)")
    languages = st.text_area("Languages (comma-separated)")
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    lang_list = [l.strip() for l in languages.split(",") if l.strip()]
    st.markdown("🖌️ Color Theme")
    theme_color = st.color_picker("Pick a theme color", "#f0f0f0")

# Main form (Right 2/3)
st.subheader("👤 Personal Details")
name = st.text_input("Full Name")
email = st.text_input("Email")

st.subheader("🎓 Education")
education = []
for level in ["High School", "Bachelor's", "Master's", "PhD/Other"]:
    with st.expander(f"{level}"):
        school = st.text_input(f"{level} - Institution")
        start = st.date_input(f"{level} - Start Date")
        ongoing = st.checkbox(f"{level} - Ongoing")
        end = None if ongoing else st.date_input(f"{level} - End Date")
        if school:
            education.append({
                "level": level,
                "institution": school,
                "start": str(start),
                "end": "Ongoing" if ongoing else str(end)
            })

st.subheader("💼 Work Experience")
experience = []
for i in range(3):  # up to 3 experiences
    with st.expander(f"Job {i+1}"):
        job = st.text_input(f"Job {i+1} - Title/Role")
        desc = st.text_area(f"Job {i+1} - Description")
        start = st.date_input(f"Job {i+1} - Start Date", key=f"jobstart{i}")
        ongoing = st.checkbox(f"Job {i+1} - Ongoing", key=f"ongoing{i}")
        end = None if ongoing else st.date_input(f"Job {i+1} - End Date", key=f"jobend{i}")
        if job and desc:
            experience.append({
                "title": job,
                "desc": desc,
                "start": str(start),
                "end": "Ongoing" if ongoing else str(end)
            })

# Generate Resume
if st.button("📝 Generate PDF Resume"):
    with st.spinner("Generating..."):

        # Image Base64 Encoding
        img_base64 = ""
        if photo:
            img_bytes = photo.read()
            img_base64 = base64.b64encode(img_bytes).decode()

        # Jinja2 HTML Template
        template_path = Path("resume_template.html")
        html_template = Template(template_path.read_text())

        html = html_template.render(
            name=name,
            email=email,
            skills=skill_list,
            languages=lang_list,
            education=education,
            experience=experience,
            color=theme_color,
            photo=img_base64
        )

        Path("resume.html").write_text(html)
        HTML("resume.html").write_pdf("resume.pdf")


        with open("resume.pdf", "rb") as f:
            pdf_data = f.read()
        st.success("✅ Resume generated!")
        st.download_button("📥 Download PDF", pdf_data, "resume.pdf")
