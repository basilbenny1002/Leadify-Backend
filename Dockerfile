FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

WORKDIR /app

# 1) Install OS deps: venv support, psycopg2 build tools, + Node.js/npm
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3-venv python3-full libpq-dev python3-dev gcc \
      nodejs npm \
 && rm -rf /var/lib/apt/lists/*

# 2) Create & activate venv so pip can install freely
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" 
   
# 3) Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# 4) Copy code & install Playwright browsers
COPY . .
RUN playwright install

# 5) Install your JS dependencies with npm
WORKDIR /app/Scrapers/JS_components
RUN npm install \
 && npm fund \
 && PUPPETEER_SKIP_DOWNLOAD=false npm install \
 && npm install puppeteer puppeteer-extra puppeteer-extra-plugin-stealth

# 6) Back to root, expose port, run
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn","main:app","--host=0.0.0.0","--port=8000"]