"""
GitHub Profile Analyzer — Flask Backend
=========================================
Handles GitHub API calls, profile analysis, and PDF report generation.
Serves a JSON API and PDF export endpoints consumed by the web interface.

Author: Adarsh Yadav
"""

import os
from io import BytesIO
from datetime import datetime
from collections import Counter

from flask import Flask, render_template, jsonify, request, send_file
import requests

from report_generator import build_report_pdf

app = Flask(__name__)

BASE_URL = "https://api.github.com"

# Optional: set your GitHub token as an environment variable to raise
# the rate limit from 60/hour to 5,000/hour.
#   Windows (PowerShell):  $env:GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
#   Mac/Linux:              export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
REQUEST_TIMEOUT = 15


# -----------------------------
# GITHUB API HELPERS
# -----------------------------
def get_user_data(username):
    try:
        response = requests.get(
            f"{BASE_URL}/users/{username}", headers=HEADERS, timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException:
        return None, "Could not connect to GitHub. Please try again."
    if response.status_code == 404:
        return None, "User not found. Please check the username."
    if response.status_code in (403, 429):
        return None, "GitHub API rate limit exceeded. Please try again later."
    if response.status_code != 200:
        return None, "Something went wrong while fetching the profile."
    return response.json(), None


def get_all_repos(username):
    repos = []
    page = 1
    while True:
        try:
            response = requests.get(
                f"{BASE_URL}/users/{username}/repos",
                headers=HEADERS,
                params={"per_page": 100, "page": page, "sort": "created"},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException:
            break
        if response.status_code in (403, 429):
            break
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return repos


def get_language_bytes(full_name):
    try:
        response = requests.get(
            f"{BASE_URL}/repos/{full_name}/languages",
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        return {}
    if response.status_code != 200:
        return {}
    return response.json()


# -----------------------------
# ANALYSIS HELPERS
# -----------------------------
def aggregate_languages(repos, limit_repos=30):
    total = Counter()
    for repo in repos[:limit_repos]:
        if repo.get("fork"):
            continue
        lang_bytes = get_language_bytes(repo["full_name"])
        for lang, byte_count in lang_bytes.items():
            total[lang] += byte_count
    return total


def get_coding_personality(user_data, repos):
    created_year = int(user_data.get("created_at", "2024")[:4])
    account_age = max(0, datetime.now().year - created_year)
    total_repos = len(repos)
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)

    if total_stars > 50:
        return "⭐ The Star Collector — your repos are getting noticed!"
    elif total_repos > 30:
        return "🏗️ The Builder — you just keep shipping projects!"
    elif account_age < 1:
        return "🌱 The Fresh Sprout — welcome to the GitHub journey!"
    elif total_repos < 5:
        return "🎯 The Focused One — quality over quantity!"
    else:
        return "🦉 The Steady Coder — consistent and reliable!"


def get_most_starred_repo(repos):
    non_fork = [r for r in repos if not r.get("fork")]
    pool = non_fork if non_fork else repos
    if not pool:
        return None
    return max(pool, key=lambda r: r.get("stargazers_count", 0))


def repos_per_year(repos):
    years = [r.get("created_at", "")[:4] for r in repos if r.get("created_at")]
    counts = Counter(years)
    return dict(sorted(counts.items()))


def calculate_profile_score(user_data, repos, languages):
    """Calculates a composite profile strength score (0-100) and detailed breakdown."""
    bio_score = 10 if user_data.get("bio") else 0
    location_score = 5 if user_data.get("location") else 0
    name_score = 5 if user_data.get("name") else 0
    profile_score = bio_score + location_score + name_score

    repo_count = len(repos)
    repo_score = min(30, repo_count * 2)

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    followers = user_data.get("followers", 0)
    community_score = min(30, (total_stars * 3) + min(15, followers))

    lang_count = len(languages)
    lang_score = min(20, lang_count * 4)

    total_score = profile_score + repo_score + community_score + lang_score
    total_score = min(100, max(0, total_score))

    score_breakdown = {
        "Profile Completeness": f"{profile_score}/20",
        "Repository Activity": f"{repo_score}/30",
        "Community & Stars": f"{community_score}/30",
        "Language Diversity": f"{lang_score}/20",
    }

    score_details = [
        {"category": "Profile Completeness", "score": profile_score, "max": 20},
        {"category": "Repository Activity", "score": repo_score, "max": 30},
        {"category": "Community & Stars", "score": community_score, "max": 30},
        {"category": "Language Diversity", "score": lang_score, "max": 20},
    ]

    insights = []
    if not user_data.get("bio"):
        insights.append("Add a detailed bio to your GitHub profile to introduce yourself.")
    if total_stars > 10:
        insights.append(f"Strong community recognition with {total_stars} stars across public repositories.")
    else:
        insights.append("Consider pinning your top projects and adding comprehensive README files to increase star engagement.")
    if lang_count >= 4:
        insights.append(f"Demonstrates technology versatility with experience in {lang_count} languages.")
    else:
        insights.append("Exploring additional languages can help showcase technical breadth.")
    if repo_count > 15:
        insights.append(f"Active project builder with a portfolio of {repo_count} repositories.")

    return total_score, score_breakdown, score_details, insights


# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/analyze/<username>")
def analyze(username):
    user_data, error = get_user_data(username)
    if error:
        return jsonify({"error": error}), 404 if "not found" in error.lower() else 429

    repos = get_all_repos(username)

    if not repos:
        return jsonify({
            "profile": {
                "name": user_data.get("name") or username,
                "bio": user_data.get("bio"),
                "location": user_data.get("location"),
                "avatar_url": user_data["avatar_url"],
                "followers": user_data["followers"],
                "following": user_data["following"],
                "public_repos": user_data["public_repos"],
                "html_url": user_data["html_url"],
                "account_age": datetime.now().year - int(user_data.get("created_at", "2024")[:4]),
            },
            "no_repos": True
        })

    languages = aggregate_languages(repos)
    top_repo = get_most_starred_repo(repos)
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    score, score_breakdown, score_details, insights = calculate_profile_score(user_data, repos, languages)

    result = {
        "profile": {
            "name": user_data.get("name") or username,
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "avatar_url": user_data["avatar_url"],
            "followers": user_data["followers"],
            "following": user_data["following"],
            "public_repos": user_data["public_repos"],
            "html_url": user_data["html_url"],
            "account_age": datetime.now().year - int(user_data.get("created_at", "2024")[:4]),
        },
        "metrics": {
            "total_repos": len(repos),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "score": score,
        },
        "score_breakdown": score_breakdown,
        "score_details": score_details,
        "insights": insights,
        "personality": get_coding_personality(user_data, repos),
        "top_repo": {
            "name": top_repo["name"],
            "url": top_repo["html_url"],
            "stars": top_repo.get("stargazers_count", 0),
            "description": top_repo.get("description") or "No description provided.",
        } if top_repo else None,
        "languages": dict(languages.most_common(8)),
        "repos_per_year": repos_per_year(repos),
        "repos": [{
            "name": r["name"],
            "language": r.get("language") or "N/A",
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "fork": r.get("fork", False),
            "created": r.get("created_at", "")[:10],
            "url": r["html_url"],
        } for r in sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)]
    }
    return jsonify(result)


@app.route("/api/download-pdf/<username>")
def download_pdf(username):
    user_data, error = get_user_data(username)
    if error:
        return jsonify({"error": error}), 404 if "not found" in error.lower() else 429

    repos = get_all_repos(username)
    languages = aggregate_languages(repos)
    score, score_breakdown, score_details, insights = calculate_profile_score(user_data, repos, languages)

    pdf_bytes = build_report_pdf(
        user=user_data,
        repos=repos,
        score=score,
        score_breakdown=score_breakdown,
        languages=languages,
        insights=insights,
        repos_per_year=repos_per_year(repos),
    )

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"github_report_{username}.pdf"
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
