FROM python:3.12

ENV MPLCONFIGDIR=/app

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8501
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.host=0.0.0.0"]