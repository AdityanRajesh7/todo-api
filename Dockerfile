# ── Stage: base image ─────────────────────────────────────────
# We start FROM an official Python image. "slim" means it's a
# minimal Linux install — smaller image, faster to pull/push.
FROM python:3.12-slim

# ── Working directory ─────────────────────────────────────────
# All subsequent commands run from here inside the container.
WORKDIR /app

# ── Dependencies first (cache trick) ─────────────────────────
# Copy ONLY requirements.txt first. If your code changes but
# requirements don't, Docker reuses this cached layer — no
# reinstall needed. This saves minutes in CI.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Now copy your code ────────────────────────────────────────
# This layer changes every time you edit code, but the
# expensive pip install layer above is already cached.
COPY app/ ./app/

# ── Tell Docker what port the app listens on ──────────────────
# This is documentation only — it doesn't actually publish it.
# You do that with -p when running the container.
EXPOSE 8000

# ── Start command ─────────────────────────────────────────────
# CMD is what runs when someone does `docker run <image>`.
# --host 0.0.0.0 is critical: by default uvicorn only listens
# on localhost *inside* the container, which is unreachable
# from outside. 0.0.0.0 means "listen on all interfaces."
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]