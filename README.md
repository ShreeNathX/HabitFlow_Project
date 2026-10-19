# Daymark + HabitFlow

**Live site:** [Open Daymark](https://shreenathx.github.io/HabitFlow_Project/)

Daymark is an offline-first goal coach. Set a learning, fitness, wellbeing, creative, career, or personal goal and get practical daily challenges. Plans and progress are saved in the current browser.

## Static goal coach

- No account, server, or online AI required
- Goal setup includes area, timeframe, daily time, experience, and optional context
- Daily challenges include instructions and a completion check
- Progress tracking, local coach prompts, and JSON backup/restore
- Service worker caches the app after the first visit for offline use

The coach uses bundled templates and simple fixed responses. It does not guarantee expert advice; fitness and wellbeing prompts are general guidance. Stop activities that cause discomfort and consult a qualified professional for specialist advice.

The live page is deployed from GitHub Pages by the workflow in .github/workflows/pages.yml. If the link is not yet active, allow the first deployment to finish in the repository’s Actions tab.

## Existing Flask habit tracker

This repository also contains the original Flask app for tracking daily habits, check-ins, and streaks.

### Run locally

1. Create a virtual environment: python -m venv .venv
2. Activate it in PowerShell: .\.venv\Scripts\Activate.ps1
3. Install packages: pip install -r requirements.txt
4. Start the server: python app.py
5. Open http://localhost:5000

GitHub Pages hosts the static Daymark site only; it does not run the Flask backend.
