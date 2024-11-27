# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the port the app runs on
EXPOSE 5001

# Define environment variables
ENV FLASK_APP=SimulatorApp.py
ENV FLASK_ENV=development

# Command to run the Flask app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
