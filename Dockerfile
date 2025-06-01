FROM python:3.10-slim

# Create a non-root user
RUN useradd -ms /bin/bash dev
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl gnupg libglib2.0-0 libnss3 libx11-xcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxrandr2 libxtst6 libasound2 libatk1.0-0 libcups2 \
    libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libxss1 libxshmfence1 libxinerama1 \
    libjpeg62 libwebp7 libffi8 libicu72 wget \
    && apt-get clean

# Install pipenv and jupyter
RUN pip install pipenv jupyter

# Copy Pipfile & install Python packages
COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system

# ✅ Correct way to install Playwright (Python version)
RUN python -m playwright install --with-deps

# Fix permissions
RUN chown -R dev:dev /app

