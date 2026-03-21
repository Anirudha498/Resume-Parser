import re
import spacy
import os
from pdfminer.high_level import extract_text
import docx

nlp = spacy.load("en_core_web_sm")

# Common skill list
SKILLS_DB = [
    "python","java","c++","c","javascript","react","node","sql","mongodb",
    "html","css","machine learning","deep learning","tensorflow","pytorch",
    "flask","django","git","github","docker","kubernetes","aws"
]

# # Required skills for job (example)

# REQUIRED_SKILLS = [
#     "python",
#     "react",
#     "node",
#     "docker",
#     "sql",
#     "aws"
# ]

# # Job skills

# JOB_SKILLS = [
#     "python",
#     "react",
#     "node",
#     "docker",
#     "sql",
#     "aws",
#     "javascript"
# ]

# -------- TEXT EXTRACTION --------

def extract_text_from_docx(file_path):

    doc = docx.Document(file_path)

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


def get_resume_text(file_path):

    if file_path.endswith(".pdf"):
        return extract_text(file_path)

    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)

    else:
        return ""


# -------- EMAIL --------

def extract_email(text):
    match = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match[0] if match else None


# -------- PHONE --------

def extract_phone(text):
    match = re.findall(r"\+?\d[\d\s\-]{8,}\d", text)
    return match[0] if match else None


# -------- NAME --------

def extract_name(text):

    doc = nlp(text[:1000])

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    return None


# -------- SKILLS --------

def extract_skills(text):

    text = text.lower()
    found_skills = []

    for skill in SKILLS_DB:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))




# -------- EDUCATION --------

def extract_education(text):

    edu_section = re.findall(
        r"education(.*?)(experience|projects|skills)", 
        text, 
        re.S | re.I
    )

    if edu_section:
        return edu_section[0][0].strip()

    return None


# -------- EXPERIENCE --------

def extract_experience(text):

    exp_section = re.findall(
        r"experience(.*?)(education|projects|skills)",
        text,
        re.S | re.I
    )

    if exp_section:
        return exp_section[0][0].strip()

    return None


# -------- PROJECTS --------



def extract_projects(text):

    lines = text.split("\n")
    projects = []
    capture = False

    for line in lines:

        line_lower = line.lower().strip()

        # Start capturing
        if "project" in line_lower:
            capture = True
            continue

        # Stop at next section
        if capture and any(keyword in line_lower for keyword in [
            "education", "skills", "experience", "certifications", "languages", "internship"
        ]):
            break

        if capture:
            projects.append(line)

    return "\n".join(projects).strip() if projects else None




# -------- MAIN PARSER --------



def parse_resume(file_path):

    text = get_resume_text(file_path)
    
    # skills = extract_skills(text)

    data = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "projects": extract_projects(text),
       
    }
    
    

    return data

