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

    language_count = st.number_input("Number of languages", 0, 10, key="lang_count")
    lang_list = []
    for i in range(language_count):
        col1, col2 = st.columns(2)
        with col1:
            lang = st.text_input(f"Language {i+1}", key=f"lang_{i}")
        with col2:
            level = st.selectbox(f"Level {i+1}", ["Beginner", "Intermediate", "Advanced", "Fluent", "Native"], key=f"level_{i}")
        if lang:
            lang_list.append({"language": lang.strip(), "level": level})

    theme_color = st.color_picker("Pick a primary theme color", "#f0f0f0")
    secondary_color = st.color_picker("Pick a secondary color for photo box", "#cccccc")

# Personal info
st.subheader("👤 Personal Info")
name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone Number")
city = st.text_input("City")
countries = sorted([country.name for country in pycountry.countries])
country = st.selectbox("Country", countries)

# Education
st.subheader("🎓 Education")
education = []
edu_count = st.number_input("Number of Education Entries", min_value=1, max_value=10, value=1)
for i in range(edu_count):
    with st.expander(f"Education {i+1}"):
        level = st.selectbox("Education Level", ["High School", "Bachelor's", "Master's", "PhD/Other"], key=f"edulevel{i}")
        institution = st.text_input("Institution Name", key=f"school{i}")
        edu_city = st.text_input("City", key=f"educity{i}")
        edu_country = st.text_input("Country", key=f"educountry{i}")
        title = st.text_input("Title of Graduation", key=f"title{i}")
        expected = st.checkbox("Expected Graduation?", key=f"exp{i}")
        date = st.date_input("Graduation Date", key=f"date{i}")
        grad_date = f"Expected to graduate on {date}" if expected else str(date)
        if institution:
            education.append({
                "level": level,
                "institution": institution,
                "city": edu_city,
                "country": edu_country,
                "title": title,
                "date": grad_date
            })

# Experience
st.subheader("💼 Work Experience")
experience = []
exp_count = st.number_input("Number of Job Entries", min_value=1, max_value=10, value=1)
for i in range(exp_count):
    with st.expander(f"Job {i+1}"):
        job = st.text_input("Job Title", key=f"job{i}")
        job_city = st.text_input("City", key=f"jobcity{i}")
        job_country = st.text_input("Country", key=f"jobcountry{i}")
        desc = st.text_area("Description", key=f"desc{i}")
        if desc:
            correction_prompt = f"Correct grammar and spelling only: {desc}"
            correction_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": correction_prompt}],
                temperature=0
            )
            desc = correction_response.choices[0].message.content.strip()
        start = st.date_input("Start Date", key=f"jobstart{i}")
        ongoing = st.checkbox("Ongoing", key=f"jobon{i}")
        end = "Ongoing" if ongoing else str(st.date_input("End Date", key=f"jobend{i}"))
        if job:
            experience.append({
                "title": job,
                "city": job_city,
                "country": job_country,
                "desc": desc,
                "start": str(start),
                "end": end
            })
# Internships
st.subheader("🎯 Internships")
internships = []
intern_count = st.number_input("Number of internships", 0, 10, step=1, key="intern_count")
for i in range(intern_count):
    with st.expander(f"Internship {i+1}"):
        title = st.text_input("Title", key=f"intern_title_{i}")
        location = st.text_input("Location", key=f"intern_loc_{i}")
        start = st.date_input("Start Date", key=f"intern_start_{i}")
        end = st.date_input("End Date", key=f"intern_end_{i}")
        internships.append({"title": title, "location": location, "start": str(start), "end": str(end)})

# Trainings
st.subheader("📚 Trainings")
trainings = []
train_count = st.number_input("Number of trainings", 0, 10, step=1, key="train_count")
for i in range(train_count):
    with st.expander(f"Training {i+1}"):
        title = st.text_input("Title", key=f"train_title_{i}")
        location = st.text_input("Location", key=f"train_loc_{i}")
        start = st.date_input("Start Date", key=f"train_start_{i}")
        end = st.date_input("End Date", key=f"train_end_{i}")
        trainings.append({"title": title, "location": location, "start": str(start), "end": str(end)})

# Certificates
st.subheader("📜 Certificates")
certificates = []
cert_count = st.number_input("Number of certificates", 0, 10, step=1, key="cert_count")
for i in range(cert_count):
    with st.expander(f"Certificate {i+1}"):
        title = st.text_input("Certificate Title", key=f"cert_title_{i}")
        date = st.date_input("Date", key=f"cert_date_{i}")
        certificates.append({"title": title, "date": str(date)})

# Manual Summary Input
st.subheader("📝 Summary")
manual_summary = st.text_area("✍️ Your Summary", value=st.session_state.get("manual_summary", ""))

# Save manual summary to session
st.session_state["manual_summary"] = manual_summary

# AI Summary
if st.button("🤖 Generate AI Summary"):
    ai_prompt = f"Write a professional summary based on this text: {manual_summary}" if manual_summary else \
                f"Generate a short professional summary based on the following:\nName: {name}\nEmail: {email}\nPhone: {phone}\nCity: {city}, {country}\nSkills: {skills}\nExperience: {experience}"
    ai_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": ai_prompt}],
        temperature=0.7
    )
    st.session_state["ai_summary"] = ai_response.choices[0].message.content.strip()

# Display AI Suggested Summary
if "ai_summary" in st.session_state:
    st.markdown("### 💡 AI Suggested Summary:")
    st.text_area("AI Summary", value=st.session_state["ai_summary"], key="ai_summary_display")
    if st.button("🔁 Replace My Summary With AI Version"):
        st.session_state["manual_summary"] = st.session_state["ai_summary"]


# Generate Resume
if st.button("📄 Generate HTML Resume"):
    with st.spinner("Generating..."):
        img_base64 = ""
        if photo:
            img_bytes = photo.read()
            img_base64 = base64.b64encode(img_bytes).decode()

        summary = st.session_state.get("manual_summary", "")

        template_path = Path("resume_template.html")
        html_template = Template(template_path.read_text())

        html = html_template.render(
            name=name,
            email=email,
            phone=phone,
            city=city,
            country=country,
            skills=skills.split("\n"),
            languages=lang_list,
            education=education,
            experience=experience,
            summary=summary,
            color=theme_color,
            secondary=secondary_color,
            photo=img_base64
        )

        st.success("✅ Resume generated!")
        st.download_button("📥 Download HTML Resume", html, "resume.html", mime="text/html")

