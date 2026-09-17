# 🐙 GitHub Developer Report Card

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![Chart.js](https://img.shields.io/badge/Charts-Chart.js-F5788D.svg)](https://www.chartjs.org/)
[![ReportLab](https://img.shields.io/badge/PDF-ReportLab-red.svg)](https://www.reportlab.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A data-driven web application that analyzes public GitHub profiles, turns repository activity into meaningful metrics, visualizes developer patterns, and generates a downloadable PDF report card.

## 📌 Overview

**GitHub Developer Report Card** is a Python + Flask analytics project built around the GitHub REST API.

Enter a public GitHub username and the application collects profile and repository data, processes it, calculates profile-level metrics, displays interactive analytics, and generates a structured PDF report.

The project focuses on **Data Analytics, Data Science, API integration, data visualization, and reporting** rather than machine learning.

---

## ✨ Features

### 👤 GitHub Profile Analysis
- Fetches public GitHub profile information.
- Displays followers, following, public repositories, bio, location, and account age.
- Provides a direct link to the analyzed GitHub profile.

### 📊 Developer Analytics
- Total repositories
- Total stars ⭐
- Total forks 🍴
- Account age
- Profile strength score
- Repository activity by year

### 💻 Technology Analysis
- Collects language statistics from public repositories.
- Excludes forked repositories from code-volume aggregation.
- Displays language distribution using an interactive Chart.js visualization.
- Provides a language-level data table.

### 🎯 Profile Strength Score
The application calculates a **0–100 profile score** using public GitHub signals such as:

- Profile completeness
- Repository activity
- Community engagement and stars
- Language diversity

> **Important:** The score represents public GitHub profile/activity signals. It is not a measure of programming ability, skill level, or developer worth.

### 🧠 Developer Insights
The application generates simple profile insights based on the analyzed GitHub data and highlights areas that can be improved.

### 📚 Repository Explorer
- Search repositories
- Filter source repositories/forks
- Sort repositories
- View stars, forks, language, description, and repository links

### 📄 PDF Report Card
Generate a downloadable PDF containing:

- Profile overview
- Profile strength score
- Score breakdown
- Technology/language analysis
- Language chart
- Repository activity chart
- Repository summary
- Developer insights

---

## 🖥️ Screenshots

### PDF Report Card

The generated PDF combines the main profile metrics, analytics, charts, repository information, and insights into a shareable report.

![PDF Report Card](screenshots/pdf-report.png)

> **Dashboard preview:** Run the application locally and use the GitHub username search to view the interactive dashboard. A dashboard screenshot can be added to `screenshots/dashboard.png` when publishing a deployment/demo version.

---

## 🔄 How It Works

```text
                GitHub Username
                       │
                       ▼
               GitHub REST API
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
    Profile Data              Repository Data
          │                         │
          └────────────┬────────────┘
                       ▼
                Data Processing
                       │
                       ▼
              Feature Engineering
                       │
          ┌────────────┼─────────────┐
          ▼            ▼             ▼
       Metrics      Analytics     Scoring
          │            │             │
          └────────────┼─────────────┘
                       ▼
             Interactive Dashboard
                       │
                       ▼
                PDF Report Card
```

### Processing flow

1. **Data Collection** — Fetch public profile and repository data from GitHub.
2. **Data Processing** — Organize repository information and aggregate language statistics.
3. **Feature Engineering** — Derive metrics such as repository count, stars, forks, account age, and language diversity.
4. **Analysis** — Examine technology distribution and repository creation trends.
5. **Scoring** — Combine selected public GitHub signals into a 0–100 profile score.
6. **Visualization** — Present the results through interactive dashboard charts and tables.
7. **Reporting** — Convert the analyzed results into a downloadable PDF report card.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Backend logic and data processing |
| **Flask** | Web application and API routes |
| **Requests** | GitHub REST API requests |
| **Chart.js** | Interactive browser visualizations |
| **ReportLab** | PDF report generation |
| **Matplotlib** | Charts embedded in the PDF |
| **HTML/CSS** | Dashboard interface |
| **JavaScript** | Frontend interaction and rendering |
| **GitHub REST API** | Public GitHub data source |

---

## 📁 Project Structure

```text
GitHub-Developer-Report-Card/
│
├── app.py                    # Flask application and GitHub API logic
├── report_generator.py       # PDF report and chart generation
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── LICENSE                   # MIT License
├── .gitignore                # Ignored files and secrets
│
├── static/
│   ├── script.js             # Frontend logic and Chart.js integration
│   └── style.css             # Dashboard styling
│
├── templates/
│   └── index.html            # Main Flask template
│
└── screenshots/
    └── pdf-report.png        # PDF report preview
```

---

## 🚀 Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Adarsh8158/GitHub-Developer-Report-Card.git
cd GitHub-Developer-Report-Card
```

### 2. Create a virtual environment

**Windows — PowerShell**

```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Enter a public GitHub username and click **Analyze Profile**.

---

## 🔐 GitHub API Rate Limits

The application works without a token using GitHub's public unauthenticated API access.

For development/testing, this is sufficient for occasional requests. GitHub's unauthenticated REST API limit is approximately **60 requests per hour per IP**.

The application also supports an optional `GITHUB_TOKEN` environment variable for authenticated API requests.

### Windows PowerShell

```powershell
$env:GITHUB_TOKEN="your_personal_access_token"
python app.py
```

### macOS / Linux

```bash
export GITHUB_TOKEN="your_personal_access_token"
python app.py
```

**Never commit a real token to GitHub.** Keep secrets in environment variables or another secret-management mechanism.

---

## 📄 PDF Report Details

The PDF is generated dynamically by `report_generator.py` using **ReportLab**.

### Report sections

**1. Profile Overview**
- Name and username
- Bio
- Followers/following
- Public repository count
- Account creation date
- GitHub profile URL

**2. Profile Strength Score**
- Overall 0–100 score
- Category-wise score breakdown
- Explanation that the score is based on public GitHub signals

**3. Technology Analysis**
- Top programming languages by code volume
- Language chart
- Language statistics table

**4. Repository Activity**
- Repository creation trend by year
- Growth/activity chart

**5. Repository Analysis**
- Top repositories
- Language
- Stars
- Forks

**6. Developer Insights**
- Automatically generated observations and improvement suggestions

---

## 📊 Example Use Case

A student, recruiter, mentor, or developer can enter a GitHub username and quickly get a structured view of the public profile.

Instead of manually checking several GitHub pages, the application brings profile information, repository metrics, technology distribution, activity trends, and a downloadable report into one dashboard.

---

## 🎯 Project Goals

This project was built to demonstrate practical skills in:

- Working with REST APIs
- Collecting real-world data
- Data processing and aggregation
- Feature engineering
- Exploratory analysis
- Data visualization
- Metric and scoring design
- Python backend development
- Frontend integration
- Automated PDF reporting

---

## 🔮 Future Improvements

Possible future versions can include:

- [ ] Better and more statistically balanced scoring methodology
- [ ] Contribution/commit activity analysis
- [ ] Pull request and issue analysis
- [ ] Repository quality indicators
- [ ] More detailed developer activity trends
- [ ] Caching to reduce repeated API requests
- [ ] Authenticated GitHub API support through secure deployment configuration
- [ ] Public deployment
- [ ] Additional PDF visualizations
- [ ] Profile comparison mode

---

## ⚠️ Limitations

- Analysis is based only on publicly available GitHub data.
- GitHub API rate limits can affect repeated requests.
- Language code-volume statistics are not equivalent to developer skill or expertise.
- The profile score is an analytical metric, not an objective evaluation of a developer.
- Private repositories and private activity are not included.

---

## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**Adarsh Yadav**

GitHub: [@Adarsh8158](https://github.com/Adarsh8158)
