FROM python:3.9.21-alpine

ENV API_URL=""
ENV API_TOKEN=""
ENV MPLCONFIGDIR=/app

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install pyarrow==9.0.0
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8004
CMD python streamlit run app.py --server.port=8004 --server.host=0.0.0.0
