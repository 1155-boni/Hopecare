FROM python:3.12-slim

# Install system dependencies for psycopg2 and build tools
RUN apt-get update && apt-get install -y gcc libpq-dev build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python create_admin.py && gunicorn hopecare_project.wsgi:application --bind 0.0.0.0:$PORT"]
