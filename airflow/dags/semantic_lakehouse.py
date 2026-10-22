import os
from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
PACKAGES="org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.12.0,org.apache.iceberg:iceberg-aws-bundle:1.12.0,io.openlineage:openlineage-spark_2.12:1.54.0"
HOST_PATH=os.environ.get("LAKEHOUSE_HOST_PATH")
if not HOST_PATH:
    raise RuntimeError("Defina LAKEHOUSE_HOST_PATH com o caminho absoluto do projeto no host")
def command(job):
    return f"/opt/spark/bin/spark-submit --packages {PACKAGES} --conf spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener --conf spark.openlineage.transport.type=kafka --conf spark.openlineage.transport.topicName=openlineage.events --conf spark.openlineage.transport.properties.bootstrap.servers=redpanda:9092 --conf spark.openlineage.transport.properties.key.serializer=org.apache.kafka.common.serialization.StringSerializer --conf spark.openlineage.transport.properties.value.serializer=org.apache.kafka.common.serialization.StringSerializer --conf spark.openlineage.namespace=semantic-lakehouse /opt/lakehouse/jobs/{job}"
def task(task_id,job):
    mounts=[Mount(source=HOST_PATH,target="/opt/lakehouse",type="bind"),Mount(source="semantic-lakehouse_ivy-cache",target="/home/spark/.ivy2",type="volume")]
    return DockerOperator(task_id=task_id,image="semantic-lakehouse-spark:local",command=command(job),docker_url="unix://var/run/docker.sock",network_mode="semantic-lakehouse_default",auto_remove="success",mounts=mounts)
with DAG("semantic_lakehouse",start_date=datetime(2026,1,1),schedule="@daily",catchup=False,tags=["iceberg","semantic","ai-ready"]) as dag:
    bronze=task("ingest_bronze","ingest_bronze.py"); silver=task("transform_silver","transform_silver.py"); gold=task("build_gold","build_gold.py"); semantic=task("publish_semantic_graph","semantic_graph.py"); validate=task("validate_lakehouse","validate_lakehouse.py")
    bronze >> silver >> gold >> semantic >> validate
