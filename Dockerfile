# Use official Python image
FROM python:3.10-slim

# Install JDK required for Looker JDBC driver
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME for the langchain-looker-agent
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Working directory for our app
WORKDIR /app

# Copy requirement file and install deps
COPY cloud-function/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy cloud function code
COPY cloud-function/ .

# Copy the Avatica JDBC driver if provided
# Place your avatica driver jar in the drivers directory before building
COPY drivers/ /opt/driver/
ENV LOOKER_JDBC_DRIVER_PATH=/opt/driver/avatica.jar

# Default port for Cloud Run
ENV PORT=8080

# Start the Functions Framework web server
CMD ["functions-framework", "--target=hello_http", "--host", "0.0.0.0", "--port", "8080"]
