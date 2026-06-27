FROM python:3.13.5-slim

# Copy the 'uv' and 'uvx' executables from the latest uv image into /bin/ in this image
# 'uv' is a fast Python package installer and environment manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /myapp

# Add the virtual environment's bin directory to the PATH so Python tools work globally
ENV PATH="/myapp/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./

# Install dependencies exactly as locked in uv.lock, without updating them
RUN uv sync --locked

COPY app ./app
COPY data ./data
COPY deployment ./deployment

EXPOSE 8080

ENTRYPOINT ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8080"]