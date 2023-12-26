# Official Python runtime as a aparent image
FROM python:3.8-slim

# Working directory in the container
WORKDIR /app

# Copying current directory into container
COPY . /app

# Installing packages
RUN pip install --no-cache-dir -r requirments.txt

# Making port 80 available outside of the container
EXPOSE 80

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]