import re
import spacy
import os
from pdfminer.high_level import extract_text
import docx

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------------------------
# SPACY
# --------------------------------------------------

nlp = spacy.load("en_core_web_sm")


# --------------------------------------------------
# SKILLS DATABASE
# --------------------------------------------------

SKILLS_DB = {
    "python": ["python"],
    "java": ["java"],
    "c": ["c"],
    "c++": ["c++", "cpp"],

    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],

    "html": ["html", "html5"],
    "css": ["css", "css3"],

    "react": ["react", "reactjs", "react.js"],
    "node": ["node", "nodejs", "node.js"],
    "express": ["express", "expressjs"],
    "flask": ["flask"],
    "django": ["django"],

    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo db"],

    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],

    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib"],

    "git": ["git"],
    "github": ["github"],
    "docker": ["docker"],
    "aws": ["aws", "amazon web services"]
}


# --------------------------------------------------
# CLEAN TEXT
# --------------------------------------------------

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# --------------------------------------------------
# PDF / DOCX EXTRACTION
# --------------------------------------------------

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)

    text = ""

    for para in doc.paragraphs:
        if para.text.strip():
            text += para.text + "\n"

    return text


def get_resume_text(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return extract_text(file_path)

    elif extension == ".docx":
        return extract_text_from_docx(file_path)

    return ""


# --------------------------------------------------
# NAME
# --------------------------------------------------

def extract_name(text):

    doc = nlp(text[:1000])

    for ent in doc.ents:

        if ent.label_ == "PERSON":

            return ent.text.strip()

    # fallback
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    if lines:
        return lines[0]

    return None


# --------------------------------------------------
# EMAIL
# --------------------------------------------------

def extract_email(text):

    matches = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    return matches[0] if matches else None


# --------------------------------------------------
# PHONE
# --------------------------------------------------

def extract_phone(text):

    matches = re.findall(
        r"\+?\d[\d\s\-]{8,}\d",
        text
    )

    if matches:
        return matches[0].strip()

    return None


# --------------------------------------------------
# SKILLS
# --------------------------------------------------

def find_skills(text):

    text = text.lower()

    found_skills = []

    for main_skill, variations in SKILLS_DB.items():

        for variation in variations:

            pattern = r'(?<!\w)' + re.escape(
                variation.lower()
            ) + r'(?!\w)'

            if re.search(pattern, text):

                found_skills.append(main_skill)

                break

    return sorted(set(found_skills))


def extract_skills(text):

    return find_skills(text)


# --------------------------------------------------
# JOB SKILLS
# --------------------------------------------------

def extract_job_skills(job_desc):

    return find_skills(job_desc)


# --------------------------------------------------
# SECTION DETECTION
# --------------------------------------------------

SECTION_NAMES = {
    "education": [
        "education",
        "academic qualification",
        "educational background",
        "academic background"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "internship",
        "internships"
    ],

    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "project experience"
    ],

    "skills": [
        "skills",
        "technical skills",
        "technical skill",
        "technologies",
        "technology"
    ],

    "certifications": [
        "certifications",
        "certificates"
    ],

    "achievements": [
        "achievements",
        "awards"
    ],

    "languages": [
        "languages",
        "language"
    ]
}


def normalize_heading(line):

    line = line.strip().lower()

    # remove common punctuation
    line = re.sub(r'[:\-]+$', '', line)

    return line.strip()


def get_section_heading(line):

    normalized = normalize_heading(line)

    for section, headings in SECTION_NAMES.items():

        for heading in headings:

            if normalized == heading:

                return section

    return None


def extract_sections(text):

    lines = text.splitlines()

    sections = {
        "education": [],
        "experience": [],
        "projects": [],
        "skills": [],
        "certifications": [],
        "achievements": [],
        "languages": []
    }

    current_section = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        detected_section = get_section_heading(line)

        if detected_section:

            current_section = detected_section
            continue

        if current_section:

            sections[current_section].append(line)

    return sections


# --------------------------------------------------
# EDUCATION
# --------------------------------------------------

def extract_education(text):

    sections = extract_sections(text)

    education = sections["education"]

    if education:

        return "\n".join(education).strip()

    return None


# --------------------------------------------------
# EXPERIENCE
# --------------------------------------------------

def extract_experience(text):

    sections = extract_sections(text)

    experience = sections["experience"]

    if experience:

        return "\n".join(experience).strip()

    return None


# --------------------------------------------------
# PROJECTS
# --------------------------------------------------

def extract_projects(text):

    sections = extract_sections(text)

    projects = sections["projects"]

    if projects:

        return "\n".join(projects).strip()

    return None


# --------------------------------------------------
# SKILL GAP
# --------------------------------------------------

def skill_gap(candidate_skills, job_skills):

    missing = []

    for skill in job_skills:

        if skill not in candidate_skills:

            missing.append(skill)

    return missing


# --------------------------------------------------
# TF-IDF + COSINE SIMILARITY
# --------------------------------------------------

def calculate_match_score(resume_text, job_desc):

    if not job_desc:

        return 0

    resume_clean = clean_text(resume_text)

    job_clean = clean_text(job_desc)

    if not resume_clean or not job_clean:

        return 0

    documents = [
        resume_clean,
        job_clean
    ]

    tfidf = TfidfVectorizer()

    matrix = tfidf.fit_transform(documents)

    similarity = cosine_similarity(
        matrix[0:1],
        matrix[1:2]
    )

    return round(
        float(similarity[0][0]) * 100,
        2
    )


# --------------------------------------------------
# FINAL MATCH SCORE
# --------------------------------------------------

def final_match_score(
    candidate_skills,
    job_skills,
    resume_text,
    job_desc
):

    if not job_skills:

        return calculate_match_score(
            resume_text,
            job_desc
        )

    matched = len(
        set(candidate_skills)
        &
        set(job_skills)
    )

    skill_score = (
        matched / len(job_skills)
    ) * 100

    similarity_score = calculate_match_score(
        resume_text,
        job_desc
    )

    final_score = (
        0.8 * skill_score
        +
        0.2 * similarity_score
    )

    return round(float(final_score), 2)


# --------------------------------------------------
# MAIN PARSER
# --------------------------------------------------

def parse_resume(file_path, job_desc):

    # Extract complete resume text
    text = get_resume_text(file_path)

    print("\n========== RESUME TEXT ==========")
    print(text[:5000])
    print("=================================\n")

    # Skills
    skills = extract_skills(text)

    # Job description
    if job_desc and job_desc.strip():

        job_skills = extract_job_skills(job_desc)

        match_score = final_match_score(
            skills,
            job_skills,
            text,
            job_desc
        )

        gap = skill_gap(
            skills,
            job_skills
        )

    else:

        job_skills = []

        match_score = 0

        gap = []

    # Sections
    education = extract_education(text)

    experience = extract_experience(text)

    projects = extract_projects(text)

    # Final data
    data = {

        "name": extract_name(text),

        "email": extract_email(text),

        "phone": extract_phone(text),

        "skills": skills,

        "education": education,

        "experience": experience,

        "projects": projects,

        "match_score": match_score,

        "job_skills": job_skills,

        "skill_gap": gap
    }

    return data