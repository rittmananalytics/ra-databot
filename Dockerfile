FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y wget openjdk-17-jre-headless && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

WORKDIR /app

COPY cloud-function/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Download Looker JDBC driver
RUN mkdir drivers && \
    cd drivers && \
    wget https://github.com/looker-open-source/calcite-avatica/releases/download/avatica-1.26.0-looker/avatica-1.26.0-looker.jar

ENV LOOKER_JDBC_DRIVER_PATH=/app/drivers/avatica-1.26.0-looker.jar

COPY cloud-function/ .

ENV PORT=8080
CMD ["functions-framework", "--target=hello_http", "--host", "0.0.0.0", "--port", "8080"]
