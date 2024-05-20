# Use an official Python runtime as a parent image
FROM python:3.8
# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /code/
# Install Nginx
RUN apt-get update && apt-get install -y nginx && apt-get clean
COPY nginx.conf /etc/nginx/sites-available/default
RUN python manage.py collectstatic --noinput
# Expose port 80 to the outside world
EXPOSE 80
# Run Gunicorn and Nginx
CMD ["sh", "-c", "nginx && gunicorn BO_ZipCode.wsgi:application --bind 0.0.0.0:8000"]