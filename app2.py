import streamlit as st
import openai
from datetime import datetime
from jinja2 import Template
import base64
from pathlib import Path

st.set_page_config(layout="wide")
st.title("📄 Smart Resume Builder (HTML Download)")

# API key
with st.sidebar:
    st.session_state["api_key"] = st.text_input("place your api key here", type="password")

if not st.session_state["api_key"]:
    st.error("❌ No API key provided.")
    st.stop()

client = openai.OpenAI(api_key=st.session_state["api_key"])

# Upload profile photo
photo = st.file_uploader("Upload a profile photo (JPG/PNG)", type=["jpg", "jpeg", "png"])

# Sidebar inputs
with st.sidebar:
    st.header("🧠 Skills & 🌐 Languages")
    skills = st.text_area("Enter one skill per line")
    skill_list = [s.strip() for s in skills.split("\n") if s.strip()]

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

    theme_color = st.color_picker("Pick a theme color", "#f94144")
    secondary_color = st.color_picker("Pick secondary color (photo background)", "#f3722c")

# Personal info
st.subheader("👤 Personal Info")
name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone Number")
city = st.text_input("City")
country = st.text_input("Country")

# Education
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

# Work experience
st.subheader("💼 Work Experience")
if "job_count" not in st.session_state:
    st.session_state.job_count = 1

experience = []
for i in range(st.session_state.job_count):
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

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("➕ Add Job"):
        st.session_state.job_count += 1
with col2:
    if st.session_state.job_count > 1 and st.button("➖ Remove Last Job"):
        st.session_state.job_count -= 1

# --- Optional Internships ---
st.subheader("🎓 Internships (optional)")
internships = []
num_interns = st.number_input("How many internships?", min_value=0, max_value=5, value=0, step=1)
for i in range(num_interns):
    with st.expander(f"Internship #{i+1}"):
        title = st.text_input(f"Internship #{i+1} - Title", key=f"int_title{i}")
        location = st.text_input(f"Internship #{i+1} - Location", key=f"int_loc{i}")
        start = st.date_input(f"Internship #{i+1} - Start Date (optional)", key=f"int_start{i}")
        end = st.date_input(f"Internship #{i+1} - End Date (optional)", key=f"int_end{i}")
        if title and location:
            internships.append({
                "title": title,
                "location": location,
                "start": str(start),
                "end": str(end)
            })

# --- Optional Training ---
st.subheader("📘 Training (optional)")
training = []
num_train = st.number_input("How many trainings?", min_value=0, max_value=5, value=0, step=1)
for i in range(num_train):
    with st.expander(f"Training #{i+1}"):
        title = st.text_input(f"Training #{i+1} - Title", key=f"train_title{i}")
        location = st.text_input(f"Training #{i+1} - Location", key=f"train_loc{i}")
        start = st.date_input(f"Training #{i+1} - Start Date (optional)", key=f"train_start{i}")
        end = st.date_input(f"Training #{i+1} - End Date (optional)", key=f"train_end{i}")
        if title and location:
            training.append({
                "title": title,
                "location": location,
                "start": str(start),
                "end": str(end)
            })

# --- Optional Certificates ---
st.subheader("📄 Certificates (optional)")
certificates = []
num_cert = st.number_input("How many certificates?", min_value=0, max_value=10, value=0, step=1)
for i in range(num_cert):
    with st.expander(f"Certificate #{i+1}"):
        title = st.text_input(f"Certificate #{i+1} - Title", key=f"cert_title{i}")
        date = st.date_input(f"Certificate #{i+1} - Date", key=f"cert_date{i}")
        if title:
            certificates.append({
                "title": title,
                "date": str(date)
            })

# AI-generated Summary
st.subheader("🧠 Professional Summary")
summary = st.session_state.get("summary", "")

if st.button("✍️ Generate Summary with AI"):
    with st.spinner("Generating a smart summary from your resume..."):
        resume_content = f"""
        Name: {name}
        Email: {email}
        Phone: {phone}
        Location: {city}, {country}
        Skills: {skill_list}
        Languages: {lang_list}
        Education: {education}
        Experience: {experience}
        Internships: {internships}
        Training: {training}
        Certificates: {certificates}
        """
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": f"Generate a short, professional 2-3 line summary for a resume based on this:\n\n{resume_content}"}
            ],
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
        st.session_state["summary"] = summary

summary = st.text_area("Edit your summary below", summary, height=150)
if st.button("✅ Use this Summary"):
    st.session_state["final_summary"] = summary

# Generate resume
if st.button("📝 Generate HTML Resume"):
    with st.spinner("Generating..."):
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
            internships=internships,
            training=training,
            certificates=certificates,
            color=theme_color,
            secondary=secondary_color,
            summary=st.session_state.get("final_summary", "")
        )

        st.success("✅ Resume generated!")
        st.download_button("📥 Download HTML Resume", html, "resume.html", mime="text/html")
