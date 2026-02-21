# AssignTaskApp 📋

A simple Streamlit task assignment app. Anyone with a `@mathco.com` email can assign tasks to `vivek.joon@mathco.com`.

## Quick Start (Local)

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Setup

### 1. GitHub Gist (Persistent Storage)
1. Go to [gist.github.com](https://gist.github.com) and create a **secret** gist.
2. Add a file named `tasks.json` with content: `[]`
3. Save the gist and copy the **Gist ID** from the URL.
4. Create a [GitHub Personal Access Token](https://github.com/settings/tokens) with `gist` scope.

### 2. Configure Secrets (Securely)
**Important:** Do NOT commit your `secrets.toml` file to GitHub. It is already added to `.gitignore`.

**For local development:**
Edit `.streamlit/secrets.toml` on your machine:
```toml
vivek_password = "[YOUR_PASSWORD]"
github_token = "[YOUR_GITHUB_TOKEN]"
gist_id = "[YOUR_GIST_ID]"
```

**For Streamlit Community Cloud (Deployment):**
1. Push this repo to GitHub (excluding `secrets.toml`).
2. Go to your app dashboard on [share.streamlit.io](https://share.streamlit.io).
3. Go to **Settings → Secrets**.
4. Paste the content of your local `secrets.toml` into the text box and save.

## Deploy to Streamlit Community Cloud
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → select `app.py`
4. Add your secrets in **Settings → Secrets** (same format as `secrets.toml`)
5. Deploy!

> ⚠️ **Do not** commit `.streamlit/secrets.toml` to a public repo. Add it to `.gitignore`.
