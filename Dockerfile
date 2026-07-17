FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends graphviz octave && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# Legacy Streamlit UI (prefer docker-compose for the FastAPI + React stack)
CMD ["streamlit", "run", "frontend_streamlit/home_page.py", "--server.port=8501", "--server.address=0.0.0.0"]
