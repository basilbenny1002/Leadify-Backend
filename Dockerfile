FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

# Set working directory
WORKDIR /app

# 1) Install OS-level build dependencies for psycopg2
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libpq-dev python3-dev gcc \
 && rm -rf /var/lib/apt/lists/*

# Copy all files
COPY . .

# Install Python deps
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install

# Go into JS folder and install Node deps
WORKDIR /app/Scrapers/JS_components

RUN chmod +x ./render-build.sh && \
    ./render-build.sh && \
    npm install && \
    npm fund && \
    PUPPETEER_SKIP_DOWNLOAD=false npm install && \
    npm install puppeteer puppeteer-extra puppeteer-extra-plugin-stealth

# Go back to app root
WORKDIR /app

# Expose port for uvicorn
EXPOSE 8000

# Run your API
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
