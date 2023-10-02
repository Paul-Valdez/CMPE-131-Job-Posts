# Use the official Python image as the base image
FROM python:3.11.5-alpine3.18

# Set the working directory to /workspace
WORKDIR /workspace

# Copy the contents of your Jenkins workspace into the Docker image
COPY . /workspace
