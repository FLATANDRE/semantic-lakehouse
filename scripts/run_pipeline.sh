#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts && chmod a+rwx artifacts
PACKAGES='org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.12.0,org.apache.iceberg:iceberg-aws-bundle:1.12.0,io.openlineage:openlineage-spark_2.12:1.54.0,org.apache.kafka:kafka-clients:3.7.0'
for job in ingest_bronze.py transform_silver.py build_gold.py semantic_graph.py validate_lakehouse.py; do
  docker compose run --rm spark-runner /opt/spark/bin/spark-submit --packages "$PACKAGES" \
    --conf spark.jars.ivy=/home/spark/.ivy2 \
    --conf spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener \
    --conf spark.openlineage.transport.type=kafka \
    --conf spark.openlineage.transport.topicName=openlineage.events \
    --conf spark.openlineage.transport.properties.bootstrap.servers=redpanda:9092 \
    --conf spark.openlineage.transport.properties.key.serializer=org.apache.kafka.common.serialization.StringSerializer \
    --conf spark.openlineage.transport.properties.value.serializer=org.apache.kafka.common.serialization.StringSerializer \
    --conf spark.openlineage.namespace=semantic-lakehouse "/opt/lakehouse/jobs/$job"
done
