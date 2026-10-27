FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY app.py .
COPY sample_data/ sample_data/
ENV PYTHONPATH=/app/src

EXPOSE 8501
# Point OLLAMA_URL at your host, e.g. -e OLLAMA_URL=http://host.docker.internal:11434
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
