
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
    st.session_state["api_key"] = st.text_input("Place your API key here", type="password")

if not st.session_state["api_key"]:
    st.error("❌ No API key provided.")
    st.stop()

client = openai.OpenAI(api_key=st.session_state["api_key"])

# Upload profile photo
photo = st.file_uploader("Upload a profile photo (JPG/PNG)", type=["jpg", "jpeg", "png"])

# Sidebar inputs
with st.sidebar:
    st.header("🧠 Skills & 🌐 Languages")
    skills = st.text_area("Enter each skill on a new line")
    languages_input = st.text_area("Enter languages and levels (e.g., English - Fluent)")
    skill_list = [s.strip() for s in skills.split("\n") if s.strip()]
    lang_list = []
    for line in languages_input.split("\n"):
        if "-" in line:
            lang, level = line.split("-", 1)
            lang_list.append({"language": lang.strip(), "level": level.strip()})

    theme_color = st.color_picker("Pick a primary theme color", "#f0f0f0")
    secondary_color = st.color_picker("Pick a secondary color for photo box", "#cccccc")

# Personal info
st.subheader("👤 Personal Info")
name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone Number")
city = st.text_input("City")
country = st.text_input("Country")

# Dynamic Sections Initialization
for section in ["edu", "job", "intern", "train", "cert"]:
    if f"{section}_count" not in st.session_state:
        st.session_state[f"{section}_count"] = 1

# Education
st.subheader("🎓 Education")
education = []
cols = st.columns([1, 1])
if cols[0].button("➕ Add Education"):
    if st.session_state.edu_count < 10:
        st.session_state.edu_count += 1
if cols[1].button("➖ Remove Education"):
    if st.session_state.edu_count > 1:
        st.session_state.edu_count -= 1

for i in range(st.session_state.edu_count):
    with st.expander(f"Education {i+1}"):
        level = st.selectbox(f"Level {i+1}", ["High School", "Bachelor's", "Master's", "PhD/Other"], key=f"level{i}")
        school = st.text_input(f"Institution {i+1}", key=f"school{i}")
        start = st.date_input(f"Start Date {i+1}", key=f"edu_start{i}")
        ongoing = st.checkbox(f"Ongoing {i+1}", key=f"edu_ongoing{i}")
        end = None if ongoing else st.date_input(f"End Date {i+1}", key=f"edu_end{i}")
        if school:
            education.append({
                "level": level,
                "institution": school,
                "start": str(start),
                "end": "Ongoing" if ongoing else str(end)
            })

# Work Experience
st.subheader("💼 Work Experience")
experience = []
cols = st.columns([1, 1])
if cols[0].button("➕ Add Job"):
    if st.session_state.job_count < 10:
        st.session_state.job_count += 1
if cols[1].button("➖ Remove Job"):
    if st.session_state.job_count > 1:
        st.session_state.job_count -= 1

for i in range(st.session_state.job_count):
    with st.expander(f"Job {i+1}"):
        job = st.text_input(f"Title/Role {i+1}", key=f"job_title{i}")
        desc = st.text_area(f"Description {i+1}", key=f"job_desc{i}")
        if desc:
            correction_prompt = f"Correct grammar and spelling only: {desc}"
            correction_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": correction_prompt}],
                temperature=0
            )
            desc = correction_response.choices[0].message.content.strip()
        start = st.date_input(f"Start Date {i+1}", key=f"job_start{i}")
        ongoing = st.checkbox(f"Ongoing {i+1}", key=f"job_ongoing{i}")
        end = None if ongoing else st.date_input(f"End Date {i+1}", key=f"job_end{i}")
        if job and desc:
            experience.append({
                "title": job,
                "desc": desc,
                "start": str(start),
                "end": "Ongoing" if ongoing else str(end)
            })

# Internships
st.subheader("🧪 Internships")
internships = []
cols = st.columns([1, 1])
if cols[0].button("➕ Add Internship"):
    if st.session_state.intern_count < 10:
        st.session_state.intern_count += 1
if cols[1].button("➖ Remove Internship"):
    if st.session_state.intern_count > 1:
        st.session_state.intern_count -= 1

for i in range(st.session_state.intern_count):
    with st.expander(f"Internship {i+1}"):
        title = st.text_input(f"Internship Title {i+1}", key=f"intern_title{i}")
        loc = st.text_input(f"Location {i+1}", key=f"intern_loc{i}")
        start = st.text_input(f"Start Date {i+1}", key=f"intern_start{i}")
        end = st.text_input(f"End Date {i+1}", key=f"intern_end{i}")
        if title:
            internships.append({"title": title, "location": loc, "start": start, "end": end})

# Trainings
st.subheader("🎯 Trainings")
trainings = []
cols = st.columns([1, 1])
if cols[0].button("➕ Add Training"):
    if st.session_state.train_count < 10:
        st.session_state.train_count += 1
if cols[1].button("➖ Remove Training"):
    if st.session_state.train_count > 1:
        st.session_state.train_count -= 1

for i in range(st.session_state.train_count):
    with st.expander(f"Training {i+1}"):
        title = st.text_input(f"Training Title {i+1}", key=f"train_title{i}")
        loc = st.text_input(f"Location {i+1}", key=f"train_loc{i}")
        start = st.text_input(f"Start Date {i+1}", key=f"train_start{i}")
        end = st.text_input(f"End Date {i+1}", key=f"train_end{i}")
        if title:
            trainings.append({"title": title, "location": loc, "start": start, "end": end})

# Certificates
st.subheader("📜 Certificates")
certificates = []
cols = st.columns([1, 1])
if cols[0].button("➕ Add Certificate"):
    if st.session_state.cert_count < 10:
        st.session_state.cert_count += 1
if cols[1].button("➖ Remove Certificate"):
    if st.session_state.cert_count > 1:
        st.session_state.cert_count -= 1

for i in range(st.session_state.cert_count):
    with st.expander(f"Certificate {i+1}"):
        title = st.text_input(f"Certificate Title {i+1}", key=f"cert_title{i}")
        date = st.text_input(f"Date {i+1}", key=f"cert_date{i}")
        if title:
            certificates.append({"title": title, "date": date})

# Generate HTML
if st.button("📄 Generate HTML Resume"):
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
            skills=skill_list,
            languages=lang_list,
            education=education,
            experience=experience,
            internships=internships,
            trainings=trainings,
            certificates=certificates,
            color=theme_color,
            secondary=secondary_color,
            photo=img_base64,
            summary=""
        )
        st.download_button("📥 Download HTML Resume", html, "resume.html", mime="text/html")
