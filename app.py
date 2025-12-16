import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from io import BytesIO

# Streamlit Page
st.set_page_config(page_title="Smart Resume Creator", layout="wide")


st.markdown("""
<style>
body { font-family: 'Arial', sans-serif; }
.stButton>button {
    background-color: #0A74DA;
    color: white;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    font-size: 16px;
    font-weight: bold;
}
.stButton>button:hover { background-color: #0659a0; }
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    border-radius: 6px;
    border: 1px solid #ccc;
    background-color: #F8F9FA;
    padding: 6px;
    color: #0F111A;
    box-shadow: 1px 1px 3px #ccc;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border: 1px solid #0A74DA;
    background-color: #FFFFFF;
    color: #0F111A;
    box-shadow: 2px 2px 6px #aaa;
}
</style>
""", unsafe_allow_html=True)

# Theme Selection
theme = st.radio("Theme:", ["Day", "Night"], horizontal=True)
if theme == "Day":
    primary_color = "#0F111A"
    bg_color = "#FFFFFF"
else:
    primary_color = "#FFFFFF"
    bg_color = "#0F111A"


st.markdown(
    f"""
    <div style='background-color:{bg_color}; color:{primary_color}; padding: 15px; border-radius: 8px; position: relative;'>
        <h1 style='text-align:center;'>Smart Resume Creator</h1>
        <span style='position:absolute; top:15px; right:15px; font-size:14px; color:grey;'>{theme} Theme</span>
        <p style='text-align:center;'>Generate a modern, stylish, professional resume using AI.</p>
    </div>
    """, unsafe_allow_html=True
)


API_KEY = "# Replace with your Gemini API key"  
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def safe_pdf_line(line, max_token_len=50):
    """Break long words to prevent PDF errors."""
    safe_line = ""
    for word in line.split(" "):
        if len(word) > max_token_len:
            new_word = "\u200b".join([word[i:i+max_token_len] for i in range(0, len(word), max_token_len)])
            safe_line += new_word + " "
        else:
            safe_line += word + " "
    return safe_line.strip()

def add_section(pdf, title, content, bullet_color=(0,102,204)):
    """Add section with colored bullets and header."""
    if not content.strip(): return


    pdf.set_fill_color(*bullet_color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(pdf.w - 2*pdf.l_margin, 10, f" {title} ", ln=1, fill=True)
    pdf.ln(2)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("DejaVu", "", 12)

    for line in content.split("\n"):
        line = line.strip()
        if not line: continue

        if "," in line and title.upper() in ["SKILLS", "PROJECTS"]:
            for item in line.split(","):
                pdf.set_text_color(*bullet_color)
                pdf.cell(5)  
                pdf.cell(3, 3, "\u2022")
                pdf.set_text_color(0,0,0)
                pdf.multi_cell(pdf.w - 2*pdf.l_margin - 10, 8, f" {safe_pdf_line(item.strip())}")
        else:
            pdf.multi_cell(pdf.w - 2*pdf.l_margin, 8, safe_pdf_line(line))
    pdf.ln(5)

    pdf.set_draw_color(*bullet_color)
    pdf.set_line_width(0.5)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.l_margin, pdf.get_y())
    pdf.ln(3)


def generate_resume(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI generation failed: {str(e)}"

st.subheader("Enter Your Details")
col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    linkedin = st.text_input("LinkedIn URL")
    github = st.text_input("GitHub URL")

with col2:
    skills = st.text_area("Skills (comma separated)")
    experience = st.text_area("Work Experience")
    projects = st.text_area("Projects")
    education = st.text_area("Education")


if st.button("Generate Resume"):
    if not name.strip():
        st.error("Name is required!")
    else:
        st.info("Generating AI-powered resume…")
        prompt = f"""
        Create a professional, modern, stylish resume in structured text format.

        Name: {name}
        Email: {email}
        Phone: {phone}
        LinkedIn: {linkedin}
        GitHub: {github}

        Skills: {skills}
        Experience: {experience}
        Projects: {projects}
        Education: {education}

        Write in sections: SUMMARY, SKILLS, EXPERIENCE, PROJECTS, EDUCATION.
        Tone: Professional, modern, ATS-friendly.
        """

        resume_text = generate_resume(prompt)
        st.subheader("Generated Resume")
        st.text_area("Resume Output", resume_text, height=450)


        pdf = FPDF()
        pdf.add_page()
        # Add fonts for Unicode
        pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
        pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
        pdf.add_font("DejaVu", "I", "DejaVuSans-Oblique.ttf", uni=True)
        pdf.add_font("DejaVu", "BI", "DejaVuSans-BoldOblique.ttf", uni=True)
        pdf.set_auto_page_break(auto=True, margin=15)

        page_width = pdf.w - 2*pdf.l_margin

 
        pdf.set_fill_color(0, 102, 204)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("DejaVu", "B", 22)
        pdf.cell(page_width, 15, f" {name} ", ln=1, fill=True)

        # Contact info
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("DejaVu", "I", 12)
        pdf.multi_cell(page_width, 8, safe_pdf_line(f"Email: {email} | Phone: {phone}"))
        pdf.multi_cell(page_width, 8, safe_pdf_line(f"LinkedIn: {linkedin} | GitHub: {github}"))
        pdf.ln(5)

        sections = ["SUMMARY", "SKILLS", "EXPERIENCE", "PROJECTS", "EDUCATION"]
        for sec in sections:
            if sec in resume_text:
                content = resume_text.split(sec)[1]
                next_sec_idx = len(content)
                for s in sections:
                    if s in content:
                        idx = content.index(s)
                        if idx < next_sec_idx:
                            next_sec_idx = idx
                sec_content = content[:next_sec_idx].strip()
                add_section(pdf, sec, sec_content)


        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        st.download_button(
            label="Download Stylish Professional Resume PDF",
            data=pdf_buffer,
            file_name="SmartResume_Stylish.pdf",
            mime="application/pdf"
        )
