import streamlit as st
import openai
from datetime import datetime
from jinja2 import Template
import base64
from pathlib import Path

# --- CONFIG ---
st.set_page_config(layout="wide")

# --- INPUT API KEY ---
with st.sidebar:
    st.session_state["api_key"] = st.text_input("Place your API key here", type="password")

if st.session_state["api_key"]:
    client = openai.OpenAI(api_key=st.session_state["api_key"])
else:
    st.error("No API key provided.")

# --- PROFILE INFO ---
st.title("📄 Smart Resume Builder")
photo = st.file_uploader("Upload your photo", type=["jpg", "jpeg", "png"])
name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone Number")
city = st.text_input("City")
country = st.text_input("Country")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎯 Skills")
    skills = st.text_area("Skills (comma-separated)")
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]

    st.header("🌐 Languages")
    language_levels = ["A1 (Beginner)", "A2 (Elementary)", "B1 (Intermediate)", "B2 (Upper-Intermediate)", "C1 (Advanced)", "C2 (Proficient)"]
    lang_list = []
    if "lang_count" not in st.session_state:
        st.session_state.lang_count = 1

    for i in range(st.session_state.lang_count):
        cols = st.columns([2, 2])
        with cols[0]:
            lang = st.text_input(f"Language #{i+1}", key=f"lang{i}")
        with cols[1]:
            level = st.selectbox(f"Level #{i+1}", language_levels, key=f"level{i}")
        if lang:
            lang_list.append({"language": lang, "level": level})

    if st.session_state.lang_count < 10:
        if st.button("➕ Add Language"):
            st.session_state.lang_count += 1

    theme_color = st.color_picker("🎨 Pick a theme color", "#f94144")
    secondary_color = st.color_picker("🟪 Secondary color (photo background)", "#f3722c")

# --- EDUCATION ---
st.header("🎓 Education")
education = []
for level in ["High School", "Bachelor's", "Master's", "PhD/Other"]:
    with st.expander(level):
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

# --- EXPERIENCE ---
st.header("💼 Work Experience")
experience = []
for i in range(3):
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

# --- HTML GENERATION BUTTON ---
if st.button("💾 Generate HTML Resume"):
    with st.spinner("Creating your resume..."):
        img_base64 = ""
        if photo:
            img_bytes = photo.read()
            img_base64 = base64.b64encode(img_bytes).decode()

        template_path = Path("resume_template.html")
        html_template = Template(template_path.read_text())

        html = html_template.render(
            name=name,
            email=email,
            phone=phone,
            city=city,
            country=country,
            photo=img_base64,
            skills=skill_list,
            languages=lang_list,
            education=education,
            experience=experience,
            color=theme_color,
            secondary=secondary_color
        )

        with open("resume.html", "w", encoding="utf-8") as f:
            f.write(html)
        st.success("✅ Resume generated!")
        st.download_button("📥 Download HTML Resume", html, "resume.html")
