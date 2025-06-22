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
    st.header("🧠 Skills")
    skills = st.text_area("Enter each skill on a new line")
    skill_list = [s.strip() for s in skills.split("\n") if s.strip()]

# Country dropdown
all_countries = sorted([country.name for country in pycountry.countries])

# Personal info
st.subheader("👤 Personal Info")
name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone Number")
country = st.selectbox("Country", all_countries)
city = st.text_input("City")

# Language proficiency with add/remove
st.subheader("🌐 Languages")
if "languages" not in st.session_state:
    st.session_state.languages = []

lang_options = ["Beginner", "Elementary", "Intermediate", "Upper Intermediate", "Advanced", "Fluent", "Native"]

for i, lang in enumerate(st.session_state.languages):
    cols = st.columns([2, 2, 1])
    lang_name = cols[0].text_input(f"Language {i+1}", value=lang.get("language", ""), key=f"lang_{i}_name")
    lang_level = cols[1].selectbox(f"Level", lang_options, index=lang_options.index(lang.get("level", "Intermediate")), key=f"lang_{i}_level")
    if cols[2].button("❌", key=f"remove_lang_{i}"):
        st.session_state.languages.pop(i)
        st.experimental_rerun()
    else:
        st.session_state.languages[i] = {"language": lang_name, "level": lang_level}

if len(st.session_state.languages) < 10:
    if st.button("➕ Add Language"):
        st.session_state.languages.append({"language": "", "level": "Intermediate"})

# Color theme
theme_color = st.color_picker("Pick a primary theme color", "#f0f0f0")
secondary_color = st.color_picker("Pick a secondary color for photo box", "#cccccc")

# Education Section
st.subheader("🎓 Education")
if "education" not in st.session_state:
    st.session_state.education = []

for i, edu in enumerate(st.session_state.education):
    with st.expander(f"Education {i+1}"):
        level = st.selectbox(f"Level {i+1}", ["High School", "Bachelor's", "Master's", "PhD/Other"], index=0, key=f"level_{i}")
        institution = st.text_input(f"Institution", value=edu.get("institution", ""), key=f"institution_{i}")
        start = st.date_input(f"Start Date", value=datetime.strptime(edu.get("start", str(datetime.now().date())), '%Y-%m-%d'), key=f"edu_start_{i}")
        ongoing = st.checkbox("Ongoing", value=edu.get("end", "") == "Ongoing", key=f"edu_ongoing_{i}")
        end = None if ongoing else st.date_input(f"End Date", value=datetime.strptime(edu.get("end", str(datetime.now().date())), '%Y-%m-%d') if edu.get("end", "") != "Ongoing" else datetime.now(), key=f"edu_end_{i}")
        if st.button("Remove Education", key=f"remove_edu_{i}"):
            st.session_state.education.pop(i)
            st.experimental_rerun()
        st.session_state.education[i] = {
            "level": level,
            "institution": institution,
            "start": str(start),
            "end": "Ongoing" if ongoing else str(end)
        }

if len(st.session_state.education) < 10:
    if st.button("➕ Add Education"):
        st.session_state.education.append({"level": "", "institution": "", "start": str(datetime.now().date()), "end": str(datetime.now().date())})

# Work Experience
st.subheader("💼 Work Experience")
if "experience" not in st.session_state:
    st.session_state.experience = []

for i, job in enumerate(st.session_state.experience):
    with st.expander(f"Job {i+1}"):
        title = st.text_input(f"Title/Role", value=job.get("title", ""), key=f"job_title_{i}")
        desc = st.text_area(f"Description", value=job.get("desc", ""), key=f"job_desc_{i}")
        if desc:
            correction_prompt = f"Correct grammar and spelling only: {desc}"
            correction_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": correction_prompt}],
                temperature=0
            )
            desc = correction_response.choices[0].message.content.strip()
        start = st.date_input(f"Start Date", value=datetime.strptime(job.get("start", str(datetime.now().date())), '%Y-%m-%d'), key=f"job_start_{i}")
        ongoing = st.checkbox("Ongoing", value=job.get("end", "") == "Ongoing", key=f"job_ongoing_{i}")
        end = None if ongoing else st.date_input(f"End Date", value=datetime.strptime(job.get("end", str(datetime.now().date())), '%Y-%m-%d') if job.get("end", "") != "Ongoing" else datetime.now(), key=f"job_end_{i}")
        if st.button("Remove Job", key=f"remove_job_{i}"):
            st.session_state.experience.pop(i)
            st.experimental_rerun()
        st.session_state.experience[i] = {
            "title": title,
            "desc": desc,
            "start": str(start),
            "end": "Ongoing" if ongoing else str(end)
        }

if len(st.session_state.experience) < 10:
    if st.button("➕ Add Job"):
        st.session_state.experience.append({"title": "", "desc": "", "start": str(datetime.now().date()), "end": str(datetime.now().date())})

# Summary Section
gen_summary = st.button("🧠 Generate Summary")
summary = ""
if gen_summary:
    prompt = f"Generate a short professional summary based on the following:\nName: {name}\nEmail: {email}\nPhone: {phone}\nCity: {city}, {country}\nSkills: {', '.join(skill_list)}\nExperience: {st.session_state.experience}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    summary = response.choices[0].message.content.strip()
    st.text_area("📝 Summary (editable)", value=summary, key="summary_text")

# AI Suggestions
if st.button("🔧 Get AI Suggestions"):
    suggestion_prompt = f"Give concise suggestions to improve this resume:\nSkills: {skill_list}\nExperience: {st.session_state.experience}"
    suggestion_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": suggestion_prompt}],
        temperature=0.5
    )
    ai_suggestions = suggestion_response.choices[0].message.content.strip()
    st.markdown("### 🔍 AI Suggestions:")
    st.write(ai_suggestions)

# Generate HTML Resume
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
            languages=st.session_state.languages,
            education=st.session_state.education,
            experience=st.session_state.experience,
            summary=st.session_state.get("summary_text", summary),
            color=theme_color,
            secondary=secondary_color,
            photo=img_base64
        )

        st.success("✅ Resume generated!")
        st.download_button("📥 Download HTML Resume", html, "resume.html", mime="text/html")
