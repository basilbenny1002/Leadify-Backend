FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

# Set working directory
WORKDIR /app

# Install OS-level deps for venv & psycopg2 build
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3-venv python3-full libpq-dev python3-dev gcc \
 && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies inside the venv
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Copy application code
COPY . .

# Install Playwright browsers
RUN playwright install

# Build and install JS components
WORKDIR /app/Scrapers/JS_components
RUN npm install \
 && npm fund \
 && PUPPETEER_SKIP_DOWNLOAD=false npm install \
 && npm install puppeteer puppeteer-extra puppeteer-extra-plugin-stealth

# Return to app root, expose port, and launch
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
