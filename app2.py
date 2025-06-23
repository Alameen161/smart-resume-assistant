import streamlit as st
import openai
from datetime import datetime
from jinja2 import Template
import base64
from pathlib import Path
import pycountry

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
    skill_list = [s.strip() for s in skills.split("\n") if s.strip()]

    languages = []
    st.markdown("**Languages**")
    lang_count = st.number_input("How many languages do you want to add?", min_value=1, max_value=10, value=1)
    levels = ["Native", "Fluent", "Professional", "Intermediate", "Beginner"]
    for i in range(lang_count):
        lang = st.text_input(f"Language {i+1}")
        level = st.selectbox(f"Proficiency {i+1}", levels, key=f"level_{i}")
        if lang:
            languages.append({"language": lang, "level": level})

    theme_color = st.color_picker("Pick a primary theme color", "#f0f0f0")
    secondary_color = st.color_picker("Pick a secondary color for photo box", "#cccccc")

# Personal info
st.subheader("👤 Personal Info")
name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone Number")
country = st.selectbox("Country", sorted([c.name for c in pycountry.countries]))
city = st.text_input("City")

# Education
st.subheader("🎓 Education")
education = []
edu_count = st.number_input("Number of education entries", min_value=1, max_value=10, value=1)
for i in range(edu_count):
    with st.expander(f"Education {i+1}"):
        level = st.text_input(f"Education Level {i+1}")
        school = st.text_input(f"Institution {i+1}")
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

# Work experience
st.subheader("💼 Work Experience")
experience = []
exp_count = st.number_input("Number of work experiences", min_value=1, max_value=10, value=1)
for i in range(exp_count):
    with st.expander(f"Job {i+1}"):
        title = st.text_input(f"Job Title {i+1}")
        desc = st.text_area(f"Description {i+1}")
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
        if title and desc:
            experience.append({
                "title": title,
                "desc": desc,
                "start": str(start),
                "end": "Ongoing" if ongoing else str(end)
            })

# Internships
st.subheader("🏢 Internships")
internships = []
intern_count = st.number_input("Number of internships", min_value=0, max_value=10, value=0)
for i in range(intern_count):
    with st.expander(f"Internship {i+1}"):
        title = st.text_input(f"Internship Title {i+1}")
        location = st.text_input(f"Location {i+1}")
        start = st.date_input(f"Start Date {i+1}", key=f"intern_start{i}")
        end = st.date_input(f"End Date {i+1}", key=f"intern_end{i}")
        if title:
            internships.append({"title": title, "location": location, "start": str(start), "end": str(end)})

# Trainings
st.subheader("🏋️ Trainings")
trainings = []
training_count = st.number_input("Number of trainings", min_value=0, max_value=10, value=0)
for i in range(training_count):
    with st.expander(f"Training {i+1}"):
        title = st.text_input(f"Training Title {i+1}")
        location = st.text_input(f"Location {i+1}")
        start = st.date_input(f"Start Date {i+1}", key=f"train_start{i}")
        end = st.date_input(f"End Date {i+1}", key=f"train_end{i}")
        if title:
            trainings.append({"title": title, "location": location, "start": str(start), "end": str(end)})

# Certificates
st.subheader("📅 Certificates")
certificates = []
cert_count = st.number_input("Number of certificates", min_value=0, max_value=10, value=0)
for i in range(cert_count):
    with st.expander(f"Certificate {i+1}"):
        title = st.text_input(f"Certificate Title {i+1}")
        date = st.date_input(f"Date {i+1}", key=f"cert_date{i}")
        if title:
            certificates.append({"title": title, "date": str(date)})

# Summary
summary = ""
if st.button("🧠 Generate Summary"):
    prompt = f"Generate a short professional summary based on the following:\nName: {name}\nEmail: {email}\nPhone: {phone}\nCity: {city}, {country}\nSkills: {', '.join(skill_list)}\nExperience: {experience}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    summary = response.choices[0].message.content.strip()
    st.text_area("📝 Summary (editable)", value=summary, key="summary_text")

# AI Suggestions
if st.button("🔧 Get AI Suggestions"):
    suggestion_prompt = f"Give concise suggestions to improve this resume:\nSkills: {skill_list}\nExperience: {experience}"
    suggestion_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": suggestion_prompt}],
        temperature=0.5
    )
    ai_suggestions = suggestion_response.choices[0].message.content.strip()
    st.markdown("### 🔍 AI Suggestions:")
    st.write(ai_suggestions)

# Generate Resume
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
            languages=languages,
            education=education,
            experience=experience,
            internships=internships,
            trainings=trainings,
            certificates=certificates,
            summary=st.session_state.get("summary_text", summary),
            color=theme_color,
            secondary=secondary_color,
            photo=img_base64
        )

        st.success("✅ Resume generated!")
        st.download_button("📅 Download HTML Resume", html, "resume.html", mime="text/html")
