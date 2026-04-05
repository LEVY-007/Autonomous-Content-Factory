# Autonomous Content Factory

A multi-agent AI system that transforms a single source document into a 
complete marketing campaign — automatically and consistently.

---

## The Problem

Marketing teams manually rewrite the same content multiple times for 
different platforms — blog posts, social media threads, and email teasers. 
This repetitive process causes creative burnout, introduces factual errors, 
and delays every product launch.

---

## The Solution

A three-agent AI pipeline where:
- **Agent 1** reads the source content and extracts a verified JSON Fact-Sheet
- **Agent 2** uses the Fact-Sheet to write a blog post, social thread, and email teaser
- **Agent 3** checks every piece for hallucinations and tone issues before approving

Users can review outputs, give feedback, regenerate individual pieces, 
and download the full campaign kit — all from a clean Streamlit interface.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| UI Framework | Streamlit |
| AI Model | Llama 3.3 70B via Groq API |
| Text parsing | Python `re` module |
| Data format | JSON (Fact-Sheet) |

---

## Key Features

- Fact-Sheet extracted as structured JSON — single source of truth
- Ambiguous statement detection and flagging
- Three content formats generated simultaneously
- Agent 3 hallucination and tone check with approve / reject verdict
- User feedback and per-piece regeneration
- Mobile preview for social thread, desktop preview for blog
- Version history with timestamps
- Per-content and full campaign kit download
- API error handling with clear warning messages

---

## Setup Instructions

### 1. Clone the repository
```
git clone https://github.com/LEVY-007/Autonomous-Content-Factory.git
cd Autonomous-Content-Factory
```

### 2. Install dependencies
```
pip install streamlit groq
```

### 3. Get a free Groq API key

- Go to **console.groq.com**
- Sign up and create an API key

### 4. Run the app
```
streamlit run app.py
```

### 5. Open in browser

The app will automatically open at `http://localhost:8501`

---

## How to use

1. Paste your Groq API key in the left sidebar
2. Paste your source content in the text area
3. Click **Run Content Factory**
4. Review the fact-sheet, blog post, social thread, and email teaser
5. Give feedback and regenerate any piece you want to improve
6. Download individual files or the full campaign kit

---

## Project Structure

| File | Type | Description |
|---|---|---|
| `app.py` | Main app | Full Streamlit app with all three agents, UI, session state, downloads and version history |
| `pipeline.py` | Practice file | All three agents connected and running without a UI |
| `agent1.py` | Practice file | Agent 1 Research and Fact-check tested in isolation |
| `agent2.py` | Practice file | Agent 2 Creative Copywriter tested in isolation |
| `agent3.py` | Practice file | Agent 3 Editor-in-Chief tested in isolation |
| `test.py` | Practice file | First connection test to verify Groq API was working |
| `requirements.txt` | Config | List of Python libraries needed to run the project |
| `README.md` | Docs | This file |


---

## What I would improve with more time

- Add URL ingestion so users can paste a link instead of copying text
- Connect to Gmail to send the email teaser directly
- Add a tone selector before running so users can pick brand voice(#have given a default tone.)
- Support multiple languages for global campaigns
- Save campaign history to a database across sessions
