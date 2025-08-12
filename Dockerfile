# Start with a lightweight Python base image
FROM python:3.11-slim

# Install netcat, which is needed for the entrypoint script
RUN apt-get update && apt-get install -y netcat-openbsd

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file first to leverage Docker's layer caching
COPY ./requirements.txt /code/requirements.txt

# Install system dependencies for Tesseract OCR and pdf2image
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy your application code into the container
COPY ./app /code/app

# Copy the entrypoint script and make it executable
COPY ./entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

# The command to run your Uvicorn server
# This will be executed by the entrypoint script
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]