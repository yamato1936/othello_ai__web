FROM python:3.12-slim


WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]


COPY model.pth .