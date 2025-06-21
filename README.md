
# 📄 Smart Resume Builder (HTML Download)

[![Streamlit App](https://img.shields.io/badge/Live%20Demo-Streamlit-brightgreen)](https://smart-resume-assistant-hagbv8kxt4st77vbj5mtgu.streamlit.app/)

Smart Resume Builder is an interactive, AI-powered web app built with **Streamlit** that lets you create a professional, styled HTML resume in minutes. It allows users to input detailed personal, educational, and work information, upload a profile photo, and auto-generate a summary using **OpenAI GPT**.

---

## 🚀 Features

- 🧠 **AI Summary**: Automatically generate a short professional summary using GPT-4.
- 📷 **Profile Photo**: Upload and embed a circular profile image.
- 💼 **Work Experience**: Add/edit multiple jobs with dates and descriptions.
- 🎓 **Education**: Input multiple levels (High School to PhD).
- 🧾 **Extras**: Add internships, trainings, and certificates (optional).
- 🌐 **Languages & Skills**: Customize both with proficiency levels.
- 🎨 **Color Customization**: Choose your resume's color theme and background.
- 💾 **Export**: Download as a styled HTML resume.

---

## 🌐 Live App

👉 [Click here to try it live](https://smart-resume-assistant-hagbv8kxt4st77vbj5mtgu.streamlit.app/)

---

## 🛠️ Technologies Used

- **Streamlit** – For creating the interactive web UI
- **OpenAI API** – For generating resume summaries
- **Jinja2** – For templating HTML resumes
- **Python** – Core logic, handling user input, formatting, etc.

---

## 📦 Installation

```bash
# 1. Clone this repo
git clone https://github.com/yourusername/smart-resume-builder.git
cd smart-resume-builder

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app2.py
```

---

## 🔐 OpenAI API Key

To use the AI-generated summary feature:

1. Get your API key from [OpenAI](https://platform.openai.com/account/api-keys)
2. Paste the key into the app sidebar when prompted

---

## 📁 Project Structure

```
├── app2.py                   # Main Streamlit application
├── resume_template.html      # HTML template for the resume
├── requirements.txt          # Python dependencies
```

---

## 📄 Output

- Generates an HTML-formatted resume
- Can be downloaded instantly using the download button

---

## 👤 Authors

- **Mohammed AlAmeen**
- **Dhevesh Suresh Kumar**

---

## 📄 License

This project is licensed under the **MIT License** – feel free to use, modify, and share.

---

## 📝 To-Do (Optional Improvements)

- Add PDF export option
- AI grammar check for work descriptions
- Location validation for cities/countries
