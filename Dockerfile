# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the code file to the working directory
COPY ehailing.py .
# Run the code file when the container starts
CMD ["python", "ehailing.py"]

