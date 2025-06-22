
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

# Validate city & country with AI
if st.button("🤔 Validate Location"):
    location_prompt = f"Is this a valid city and country: {city}, {country}? Answer only 'Valid' or 'Invalid'."
    loc_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": location_prompt}],
        temperature=0
    )
    result = loc_response.choices[0].message.content.strip().lower()
    if "invalid" in result:
        st.error("❌ Invalid location. Please check spelling.")
        st.stop()
    else:
        st.success("✅ Location is valid.")

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

# Experience
st.subheader("💼 Work Experience")
experience = []
for i in range(3):
    with st.expander(f"Job {i+1}"):
        job = st.text_input(f"Job {i+1} - Title/Role")
        desc = st.text_area(f"Job {i+1} - Description")
        if desc:
            correction_prompt = f"Correct grammar and spelling only: {desc}"
            correction_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": correction_prompt}],
                temperature=0
            )
            desc = correction_response.choices[0].message.content.strip()
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

# AI Suggestions before generating resume
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

        # Load template
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
            summary=st.session_state.get("summary_text", summary),
            color=theme_color,
            secondary=secondary_color,
            photo=img_base64
        )

        st.success("✅ Resume generated!")
        st.download_button("📅 Download HTML Resume", html, "resume.html", mime="text/html")
