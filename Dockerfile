FROM ubuntu:20.04

# Define the main directory for the application
ENV MAIN_DIR=/home/main

# Create the working directory
RUN mkdir "${MAIN_DIR}"

# Set the working directory to MAIN_DIR
WORKDIR "${MAIN_DIR}"

# Set PYTHONPATH so that Python can locate your package (e.g., the "app" package if it's under MAIN_DIR)
ENV PYTHONPATH="${MAIN_DIR}"

# Update and install required packages
RUN apt-get update
RUN apt-get install -y python3.9 
RUN apt-get install -y python3.9-dev 
RUN apt-get install -y pip

# Upgrade pip and install necessary Python libraries
RUN pip install --upgrade pip
RUN pip install --upgrade cython
RUN pip install --upgrade lxml requests beautifulsoup4 pypika pytest

# Copy the entire codebase into the container
COPY . .
