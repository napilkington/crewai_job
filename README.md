# 🚀 Job Application Automation with CrewAI

Intelligent job application system powered by CrewAI and LangChain that uses AI agents to customize CVs and cover letters for specific job postings. Uses Azure OpenAI with Azure AD authentication and includes a Chrome extension for one-click LinkedIn job processing.

## ✨ Features

- 🔍 **Intelligent Job Analysis** - Extracts requirements, qualifications, and company culture from job postings
- 📝 **Smart CV Customization** - Tailors your CV to highlight relevant skills for each job
- ✉️ **Personalized Cover Letters** - Creates cover letters that connect your experience with job requirements
- 🎨 **Professional Output** - Generates PDF and JPEG versions of documents
- 🌐 **Browser Extension** - One-click processing from LinkedIn job postings
- 🔐 **Azure AD Authentication** - No API keys needed, uses Azure OpenAI

## 🛠️ Installation

```bash
# Clone and setup
git clone https://github.com/yourusername/crewai-job.git
cd crewai-job
pip install -r requirements.txt

# Configure Azure (edit with your Azure OpenAI details)
cp .env.example .env

# Authenticate with Azure
az login
```

## 📋 Prerequisites

- Python 3.8+
- Azure OpenAI access with Azure AD
- Chrome/Edge browser (for extension)
- Your base CV and cover letter as `CV.txt` and `Cover_Letter.txt`

## 🚀 Quick Start

### Option 1: Browser Extension (Recommended)

1. **Install Extension:**
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select `browser-extension` folder (or copy it to Windows Desktop first if using WSL)

2. **Start Server:**
   ```bash
   python server.py
   ```

3. **Use It:**
   - Go to any LinkedIn job posting
   - Click the extension icon
   - Click "Extract & Process Job"
   - Wait 30 seconds
   - Find documents in `output/` folder

### Option 2: Command Line

```bash
python job_application_agents.py
# Enter job URL when prompted
```

## 🤖 How It Works

Three AI agents collaborate to create tailored applications:

1. **Job Description Crawler** - Analyzes job posting and extracts key information
2. **CV Writer** - Rewrites your CV to emphasize relevant experience and skills
3. **Cover Letter Writer** - Creates personalized cover letter mentioning company and role specifics

**Example:** Original CV shows "UX/UI Developer" with e-commerce skills. For a Data Engineer role, agents transform it to "Senior Data Engineer" highlighting Databricks, PySpark, and AWS experience.

## 📂 Output

Each job generates 4 files in `output/`:
- `cv.pdf` & `cv.jpg` - Customized CV
- `cover_letter.pdf` & `cover_letter.jpg` - Tailored cover letter

## 🔧 Troubleshooting

**Extension not working:**
- Ensure server is running: `python server.py`
- Check you're on a job posting page (not search results)
- Verify Azure auth: `az account show`

**LinkedIn blocking:**
- Extension uses YOUR logged-in session, so no blocking
- If manual URL fails, use the extension or copy-paste job description

**WSL + Windows:**
- Copy extension to Windows: `cp -r browser-extension /mnt/c/Users/YOUR_USERNAME/Desktop/`
- Access output: `\\wsl$\Ubuntu\home\YOUR_USERNAME\crewai-job\output`

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

**Status:** ✅ Production Ready | **Tested:** End-to-End | **Auth:** Azure AD
