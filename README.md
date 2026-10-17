# AI Video Generator

A Streamlit starter app that accepts a short video idea, enhances it with a
LangChain pipeline, and provides a clear integration point for a text-to-video API.

## Setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r req.txt
Copy-Item .env.example .env
```

Put your OpenAI API key in `.env`, then start the app:

```powershell
streamlit run app.py
```

## Pipeline

`User idea → LangChain prompt template → selected OpenAI model → enhanced prompt → selected video provider`

The prompt step is fully functional. The text-to-video APIs differ substantially,
so `generate_video()` in `app.py` is intentionally the single, explicit place to
add credentials, provider SDK code, asynchronous job polling, and the final video URL.

Select your desired provider in the sidebar, then implement its branch in that
function. The comments include a small Replicate-shaped example.
