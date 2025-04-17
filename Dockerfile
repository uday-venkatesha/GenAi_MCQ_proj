# Use a Python base image
FROM python:3.9-slim

# Set environment variables to ensure python output is logged to the terminal
ENV PYTHONUNBUFFERED=1

# Create and set the working directory to /app
WORKDIR /app

# Copy the project requirements file into the container
COPY requirements.txt /app/

# Install the project dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Set the entrypoint for the application (e.g., running a streamlit app or a specific python script)
# Adjust this as needed to fit how you run the project (e.g., Streamlit app or testing script)
CMD ["streamlit", "run", "Streamlit.py"]
