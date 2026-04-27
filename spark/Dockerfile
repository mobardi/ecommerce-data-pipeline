FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jre-headless \
    curl \
    procps \
 && rm -rf /var/lib/apt/lists/*

RUN pip install pyspark==3.5.1

RUN mkdir -p /opt/jars && \
    curl -L -o /opt/jars/elasticsearch-spark-30_2.12-8.11.1.jar \
    https://repo1.maven.org/maven2/org/elasticsearch/elasticsearch-spark-30_2.12/8.11.1/elasticsearch-spark-30_2.12-8.11.1.jar

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PYSPARK_SUBMIT_ARGS="--jars /opt/jars/elasticsearch-spark-30_2.12-8.11.1.jar pyspark-shell"

WORKDIR /app
COPY spark_job.py /app/spark_job.py

CMD ["python", "/app/spark_job.py"]
