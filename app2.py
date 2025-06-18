import streamlit as st
import openai
from datetime import datetime
from jinja2 import Template
import base64
from pathlib import Path

st.set_page_config(layout="wide")
st.title("📄 Smart Resume Builder with Summary & Suggestions")

# API Key input
with st.sidebar:
    st.session_state["api_key"] = st.text_input("place your api key here", type="password")

# Ensure key provided
if not st.session_state["api_key"]:
    st.error("No API key provided!!")
    st.stop()

client = openai.OpenAI(api_key=st.session_state["api_key"])

# Upload Photo
photo = st.file_uploader("Upload a profile photo (JPG or PNG)", type=["jpg", "jpeg", "png"])

# Sidebar inputs
with st.sidebar:
    st.header("🧠 Skills & 🌐 Languages")
    skills = st.text_area("Skills (comma-separated)")
    languages = st.text_area("Languages (comma-separated)")
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    lang_list = [l.strip() for l in languages.split(",") if l.strip()]
    theme_color = st.color_picker("Pick a theme color", "#f0f0f0")

# Personal Info
st.subheader("👤 Personal Details")
name = st.text_input("Full Name")
email = st.text_input("Email")

# Education
st.subheader("🎓 Education")
education = []
for level in ["High School", "Bachelor's", "Master's", "PhD/Other"]:
    with st.expander(f"{level}"):
        school = st.text_input(f"{level} - Institution", key=level+"school")
        start = st.date_input(f"{level} - Start Date", key=level+"start")
        ongoing = st.checkbox(f"{level} - Ongoing", key=level+"ongoing")
        end = None if ongoing else st.date_input(f"{level} - End Date", key=level+"end")
        if school:
            education.append({
                "level": level,
                "institution": school,
                "start": str(start),
                "end": "Ongoing" if ongoing else str(end)
            })

# Experience
st.subheader("💼 Work Experience")
experience = []
for i in range(3):
    with st.expander(f"Job {i+1}"):
        job = st.text_input(f"Job {i+1} - Title/Role", key=f"job{i}")
        desc = st.text_area(f"Job {i+1} - Description", key=f"desc{i}")
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

# === Summary Section ===
st.subheader("📝 Professional Summary")

if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""

manual_summary = st.text_area("✍️ Manually write/edit your summary:", value=st.session_state.summary_text, height=150)

if st.button("🔁 Generate Summary with AI"):
    resume_data = f"""
    Name: {name}\nEmail: {email}\nSkills: {skills}\nLanguages: {languages}\nEducation: {education}\nExperience: {experience}
    """
    prompt = f"Based on the resume below, generate a compelling 3-4 sentence professional summary:\n{resume_data}"
    with st.spinner("Generating summary..."):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        ai_summary = response.choices[0].message.content
        st.session_state.summary_text = ai_summary
        manual_summary = ai_summary
        st.success("Summary generated. You can now edit it manually if needed.")

# Use updated text if user edited manually
st.session_state.summary_text = manual_summary

# Confirm inclusion in resume
include_summary = st.checkbox("✅ Include summary in resume")

# Suggestions (only visible in app)
st.subheader("💡 AI Suggestions (only shown here)")
if st.button("📌 Get AI Suggestions"):
    resume_data = f"Skills: {skills}\nLanguages: {languages}\nEducation: {education}\nExperience: {experience}"
    prompt = f"Review the following resume data and suggest 3 improvements:\n{resume_data}"
    with st.spinner("Analyzing resume..."):
        suggestion_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        suggestions = suggestion_response.choices[0].message.content
        st.info(suggestions)

# === Generate Final HTML Resume ===
if st.button("💾 Generate HTML Resume"):
    img_base64 = ""
    if photo:
        img_bytes = photo.read()
        img_base64 = base64.b64encode(img_bytes).decode()

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
        photo=img_base64,
        summary=st.session_state.summary_text if include_summary else None
    )

    Path("resume.html").write_text(html)
    st.success("✅ HTML Resume Generated!")
    st.download_button("📄 Download HTML", data=html, file_name="resume.html")
