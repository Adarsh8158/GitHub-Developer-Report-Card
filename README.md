# 🐙 GitHub Developer Report Card & Profile Analyzer

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, full-stack web application built with **Python**, **Flask**, **Chart.js**, and **ReportLab**. It fetches public data from the **GitHub REST API**, analyzes developer profiles, computes profile strength metrics, visualizes language distribution and repository trends, and exports a high-quality PDF Report Card.

---

## ✨ Features

- 📊 **Developer Profile Scoring**: Calculates a 0–100 composite score based on profile completeness, activity, community engagement, and tech stack diversity.
- 🎭 **Coding Personality Assignment**: Automatically categorizes developers into fun personality types based on their commit habits, account age, and project volume.
- 💻 **Language Breakdown**: Aggregates code volume per language across non-forked repositories and visualizes it using interactive Chart.js doughnut charts.
- 📈 **Repository Timeline**: Displays repositories created over the years in a bar chart to highlight coding consistency.
- 📄 **PDF Report Generation**: Generates clean, downloadable PDF report cards dynamically using ReportLab.
- 🛡️ **Rate Limit Handling**: Works out-of-the-box using unauthenticated requests (60 requests/hr) and supports optional `GITHUB_TOKEN` environment variable to boost rate limit to 5,000 requests/hr.

---

## 📁 Project Structure

```
GitHub-Developer-Report-Card/
├── app.py                   # Flask application routes & API endpoints
├── report_generator.py      # ReportLab PDF report generation module
├── requirements.txt         # Python dependencies
├── .gitignore               # Git ignore configuration
├── LICENSE                  # MIT License
├── README.md                # Project documentation
├── static/
│   ├── script.js            # Frontend JavaScript & Chart.js integration
│   └── style.css            # Dark mode UI styling
└── templates/
    └── index.html           # Main dashboard template
```

---

## 🛠️ Installation & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR-USERNAME/GitHub-Developer-Report-Card.git
cd GitHub-Developer-Report-Card
```

### 2. Set up a Virtual Environment (Optional but recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Set GitHub API Token
To avoid hitting GitHub API rate limits (60 requests/hour), set your personal access token:
```bash
# Windows (PowerShell)
$env:GITHUB_TOKEN="your_personal_access_token"

# Mac/Linux
export GITHUB_TOKEN="your_personal_access_token"
```

### 5. Run the application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 📄 PDF Report Architecture

The PDF generation module (`report_generator.py`) builds a structured document using ReportLab:
1. **Profile Overview**: Avatar stats, bio, account creation date, followers/following.
2. **Profile Strength Score**: Score breakdown by category with contextual notes.
3. **Technology Analysis**: Table of code volume per language in bytes.
4. **Repository Breakdown**: Top 15 repositories with star and fork counts.
5. **Developer Insights**: Actionable recommendations for profile improvement.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
