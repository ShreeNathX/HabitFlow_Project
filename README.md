# Daymark

**Live site:** [Open Daymark](https://shreenathx.github.io/HabitFlow_Project/)

Daymark turns a goal in any area—learning, fitness, creativity, career, wellbeing, or everyday habits—into a manageable daily practice. It includes a distinct, responsive interface, progress tracking, daily challenges, an AI coach, and offline-ready local suggestions.

## How it works

- Your goals, check-ins, and progress stay in the browser on your device.
- Local suggestions keep working when the AI backend is not connected.
- Connect the optional AI service from **Connect AI**. The service creates a flexible plan, daily challenges, and coach replies.
- AI output is validated and kept within a structured response shape. That reduces formatting errors but cannot guarantee that every suggestion is correct.
- Do not enter sensitive details. AI suggestions are general guidance, not medical, legal, or financial advice.

## Hosting

The front end is a static GitHub Pages site. The small Flask API is prepared as a free Render web service in `render.yaml`. Render's free web services can sleep after inactivity, so the first request may take about a minute. Usage quotas and free model availability depend on the provider and can change.

### Enable the AI coach

1. Create an OpenRouter account and an API key. Review the model/provider data policy before use; free model routes may send inputs to different providers with different retention or training practices.
2. In Render, create a Blueprint from this repository and deploy the `daymark-ai` service.
3. In the Render service environment, add `OPENROUTER_API_KEY` as a secret. The key belongs only on Render; never add it to this repository or the browser.
4. Wait for the service health check at `/health` to pass. Copy the service's `https://…onrender.com` URL.
5. Open the live site, choose **Connect AI**, paste the URL, and save.

The default model is `openai/gpt-oss-20b:free`. You can change `AI_MODEL` in Render to another currently available free model. Free-tier limits are shared by everyone using this public app, so restrict or rotate the provider key if unexpected usage appears.

### Local preview

Serve this folder over HTTP (for example, `python -m http.server 8000`) and open `http://localhost:8000`. Add `http://localhost:8000` to `FRONTEND_ORIGINS` if you use a local backend. To run the API locally, set `OPENROUTER_API_KEY` in your shell and run `python ai_service.py`.

## Privacy and safety

The browser stores goals and progress locally. The connected API receives only the current goal and the minimum context needed for a plan, challenge, or chat request. The API does not save a user profile or conversation database. The API provider and the selected model provider may process request content under their own policies. Do not share health history or other sensitive personal information.

Fitness suggestions are conservative general prompts. Stop if you feel pain and ask a qualified professional before strenuous exercise or when you have concerns about your health. AI can still make factual mistakes; verify important information.

## Original Flask tracker

The repository also retains the earlier Flask habit tracker (`app.py`). GitHub Pages publishes only the static Daymark front end; Render runs the separate AI API.
