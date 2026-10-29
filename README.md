# Task-Automation Research Agent (MLOps Experiment 10)

A Streamlit web app that searches the web with DuckDuckGo and summarizes the results into exactly three bullet points using Groq.

## Features
- Sequential workflow: search, then summarize.
- Streamlit user interface.
- Environment-variable-based API key configuration.
- Logging of received topics, request duration, and errors.
- Docker containerization.
- GitHub Actions CI: pytest checks and Docker image build.
- Deployable to a free Hugging Face Docker Space.

## Requirements
- Python 3.11
- A Groq API key (create/manage it in your Groq account; API usage limits apply)
- Git; Docker is optional for local container testing

## Run locally (Windows CMD)
```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
set GROQ_API_KEY=your_real_key_here
streamlit run app.py
```
Keep the key private. Do not paste it into source code or commit it to Git.

## Run tests
```bat
pytest -q
```

## Build and run with Docker
```bat
docker build -t task-automation-agent .
docker run --rm -p 7860:7860 -e GROQ_API_KEY=your_real_key_here task-automation-agent
```
Open http://localhost:7860.

## Deploy to Hugging Face Spaces (free tier)
1. Sign in at https://huggingface.co/ and create a new Space.
2. Choose **Docker** as the Space SDK and select the free CPU hardware option.
3. In Space **Settings → Variables and secrets**, add `GROQ_API_KEY` as a secret. Optionally add `GROQ_MODEL` as a variable.
4. Upload/push the project files to the Space repository. The included Dockerfile listens on port 7860, the standard Hugging Face Docker Space port.
5. The Space builds the Docker image and starts the app. Open the Space's public URL and test at least two topics.
6. For automatic GitHub-to-Space deployment, create a Hugging Face access token with write permission. In GitHub → Settings → Secrets and variables → Actions, add secret `HF_TOKEN`, and repository variables `HF_USERNAME` and `HF_SPACE_NAME`. The included `.github/workflows/deploy-huggingface.yml` pushes to the Space after the `Task Agent CI` workflow succeeds. Do not put the token in code.

## CI/CD notes
The included `.github/workflows/ci.yml` automatically runs tests and builds the Docker image on every push to `main` and on pull requests. This is continuous integration. To make deployment automatic too, connect GitHub to your Space using the `HF_TOKEN` secret and a deploy workflow, or use the Space repository as the deployment source.

## Logs / monitoring
The app writes request topics, duration, source count, and exceptions to standard output. In Hugging Face Spaces, inspect the Space's **Logs** view. Do not include API keys in logs.

## Pipeline
Developer edit → Git push → GitHub Actions → pytest → Docker build → Hugging Face Space build/deploy → live Streamlit app → logs.

## Troubleshooting
- `GROQ_API_KEY is missing`: configure the environment variable locally or the secret in Space settings.
- Search returns no results: retry with a more specific topic.
- Model returns other than three bullets: retry; the app reports a controlled error instead of pretending the output is valid.
- Docker command not found: install/start Docker Desktop, or deploy directly using the Hugging Face Docker Space build.
