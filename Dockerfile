FROM python:3.9-alpine
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt 
EXPOSE 8004
CMD python streamlit run app.py --server.port=8004 --server.host=0.0.0.0
