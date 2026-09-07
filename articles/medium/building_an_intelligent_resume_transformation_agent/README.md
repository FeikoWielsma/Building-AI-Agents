# 🚀 Building an Intelligent Resume Transformer with LangGraph and GPT-4o-mini

Read the complete medium article here [Building an Intelligent Resume Transformation Agent Powered by LangGraph and gpt-4o-mini](https://medium.com/towards-artificial-intelligence/building-an-intelligent-resume-transformation-agent-powered-by-langgraph-and-gpt-4o-mini-2fbb3004dcd3)

*Transform unstructured resumes into structured, searchable data using AI-powered agents*

---

## The Problem: Resume Chaos in Modern Hiring

Every recruiter knows the pain: hundreds of resumes in different formats (PDF, DOCX, TXT), inconsistent layouts, varying structures, and no easy way to search through them. Modern Applicant Tracking Systems automatically parse resumes, but parsing errors and inconsistencies are common. As a result, HR teams still spend significant time validating and correcting extracted data.

**What if we could automatically transform any resume into a structured, searchable database?**

That's exactly what this Resume Transformer Agent does.

---

## 🎯 What This Project Does

This is an **intelligent resume processing pipeline** built with **LangGraph** and **OpenAI's GPT-4o-mini** that:

1. **Parses** resumes from multiple formats (PDF, DOCX, TXT) — even image-based PDFs with OCR
2. **Extracts** structured data using AI (contact info, experience, education, skills)
3. **Validates & Enriches** the data (calculates years of experience, standardizes skills)
4. **Stores** everything in a queryable SQLite database

The result? A fully automated Applicant Tracking System (ATS) that can process resumes at scale.

---

## 📁 Project Structure

```
resume-transformer-agent/
│
├── README.md                          # This file - comprehensive project documentation
├── requirements.txt                   # Python dependencies
├── .env                              # Environment variables (API keys) - not in repo
├── .gitignore                        # Git ignore rules
│
├── resume-transformer-agent.ipynb    # Main Jupyter notebook with complete workflow
│
├── data/                             # Sample resume files for testing
│   ├── *.pdf                        # PDF resume samples
│   ├── *.docx                       # DOCX resume samples
│   └── *.txt                        # Text resume samples
│
└── resume_ats.db                     # SQLite database (auto-generated)
    ├── candidates table              # Main candidate information
    ├── experience table              # Work history entries
    ├── education table               # Educational background
    ├── skills table                  # Normalized skills
    └── certifications table          # Professional certifications
```

Please note, For simplicity and readability, this article uses the term agent to describe both Python-based workflow functions and the AI-powered extraction component. Only the extraction step uses a true AI agent backed by GPT-4o-mini, while the other agents are deterministic Python functions orchestrated within the workflow.
---

## ✨ Key Features

### 🔍 Multi-Format Resume Parsing
- **PDF Support**: Extract text from regular PDFs
- **OCR Support**: Process image-based PDFs using Tesseract
- **DOCX & TXT**: Handle Microsoft Word documents and plain text files

### 🤖 AI-Powered Data Extraction
- Uses **GPT-4o-mini** to intelligently extract structured data
- Handles various resume formats and layouts
- Normalizes data to consistent schema

### 🛠️ Intelligent Data Processing
- **Automatic Experience Calculation**: Computes total years of experience
- **Skill Standardization**: Maps skills to company taxonomy (Python, React, AWS, etc.)
- **Data Validation**: Cleans contact info, validates emails, formats dates

### 💾 Structured Database Storage
- **SQLite Database**: Efficient, portable storage
- **Normalized Schema**: Separate tables for candidates, experience, education, skills
- **Query Support**: Search by skills, experience, location, and more

### 📊 Batch Processing
- Process multiple resumes at once
- Progress tracking and error handling
- Detailed reporting of successes and failures

---

## 🏗️ Architecture: The Four-Agent Workflow

This project uses **LangGraph** to orchestrate four specialized agents in a sequential workflow:

```
┌──────────────┐
│   START      │
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│  1. PARSE       │  ← Extract raw text from file
│  Agent          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. EXTRACT     │  ← Use GPT-4o-mini to structure data
│  Agent          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. VALIDATE    │  ← Clean, enrich, standardize
│  & ENRICH       │
│  Agent          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. HITL        │  ← Manual review by human
│  HUMAN IN THE.  │
│  LOOP           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. STORE       │  ← Insert into database
│  Agent          │
└────────┬────────┘
         │
         ▼
┌──────────────┐
│    END       │
└──────────────┘
```

### Step 1: Parse Agent (Python Based function) 📄
**Responsibility**: Extract raw text from resume files

- Handles PDF, DOCX, and TXT formats
- Falls back to OCR for image-based PDFs
- Robust error handling

### Step 2: Extract Agent (LLM Powered) 🤖
**Responsibility**: Transform raw text into structured JSON

- Uses GPT-4o-mini for intelligent extraction
- Follows strict JSON schema
- Extracts: contact info, summary, experience, education, skills, certifications

### Step 3: Validate & Enrich Agent (Python Based function) ✨
**Responsibility**: Clean and enhance the data

- Validates email addresses and phone numbers
- Calculates total years of experience
- Standardizes skills to company taxonomy
- Adds metadata (processing date, version)


### Step 4: HITM  (Human in the loop) 💾
**Responsibility**: Allowing user to validate the extracted data side by side

- Creates a side by side view on the resume and the extracted fields in HTML file
- User can edit the extracted data

### Step 5: Store Agent  (Python Based function) 💾
**Responsibility**: Persist data to database

- Creates SQLite database if it doesn't exist
- Inserts candidate data across normalized tables
- Returns database ID for reference

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- (Optional) Tesseract for OCR support

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/resume-transformer-agent.git
cd resume-transformer-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key**
```bash
# Create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

4. **(Optional) Install OCR support**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Then install Python packages
pip install pytesseract pdf2image pillow
```

### Quick Start

Open the Jupyter notebook and run:

```python
from pathlib import Path

# Process a single resume
result = process_resume("data/sample_resume.pdf")

if result['success']:
    print(f"✅ Processed: {result['candidate_name']}")
    print(f"📊 Database ID: {result['database_id']}")
```

---

## 📖 Usage Examples

### Process a Single Resume

```python
result = process_resume("path/to/resume.pdf")

if result['success']:
    validated_data = result['state']['validated_data']
    print(f"Candidate: {validated_data['contact']['name']}")
    print(f"Experience: {validated_data['total_years_experience']} years")
    print(f"Skills: {', '.join(validated_data['skills'][:5])}")
```


### Query the Database

```python
# Find Python developers
search_by_skill("Python")

# Find candidates with 5+ years experience
search_by_experience(5.0)

# View all candidates
query_database()
```

---

## 🗄️ Database Schema

The system uses a normalized SQLite schema:

### `candidates` table
- Basic info: name, email, phone, location
- Links: LinkedIn, GitHub
- Metadata: total experience, processing date

### `experience` table
- Work history entries
- Company, title, dates, description
- Foreign key to candidates

### `education` table
- Educational background
- Institution, degree, field, graduation year
- Foreign key to candidates

### `skills` table
- Individual skills (normalized)
- Foreign key to candidates

### `certifications` table
- Professional certifications
- Foreign key to candidates

---

## 🎨 Advanced Features

### Skill Standardization

The system automatically maps skills to a standard taxonomy:

```python
'python' → 'Python'
'reactjs' → 'React'
'k8s' → 'Kubernetes'
'ml' → 'Machine Learning'
```

This ensures consistent skill matching across resumes.

### Experience Calculation

Automatically calculates total years of experience from work history:

```python
Job 1: 2020-01 to 2022-06  → 2.5 years
Job 2: 2022-07 to Present   → 2.5 years
Total: 5.0 years
```

### OCR Support

For image-based PDFs (scanned resumes), the system automatically:
1. Detects no text extraction
2. Converts PDF pages to images
3. Applies Tesseract OCR
4. Extracts text from images

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Orchestration** | LangGraph |
| **LLM** | OpenAI GPT-4o-mini |
| **PDF Parsing** | PyPDF2 |
| **DOCX Parsing** | python-docx |
| **OCR** | Tesseract + pdf2image |
| **Database** | SQLite3 |
| **Environment** | Python 3.8+ |

---



## 📝 License

MIT License - feel free to use this project for your own applications!

---

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- [OpenAI](https://openai.com/) for GPT-4o-mini
- [PyPDF2](https://pypdf2.readthedocs.io/) for PDF parsing
- [Tesseract](https://github.com/tesseract-ocr/tesseract) for OCR

---

## 📧 Contact

Questions? Issues? Reach out or open an issue on GitHub!

---

**Happy Resume Processing! 🎉**

*Transform chaos into structure, one resume at a time.*
