# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app/backend
COPY app.py .
COPY start.sh .

# Make 5000 for flask backend
EXPOSE 5000

ENV FLASK_APP=app.py

RUN chmod +x start.sh

CMD ["./start.sh"]
