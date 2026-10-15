from pathlib import Path
from pyspark.sql import SparkSession
CATALOG = "lakehouse"
ROOT = Path(__file__).resolve().parents[1]
def spark_session(app_name):
    return (SparkSession.builder.appName(app_name)
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config(f"spark.sql.catalog.{CATALOG}", "org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.catalog.{CATALOG}.type", "rest")
        .config(f"spark.sql.catalog.{CATALOG}.uri", "http://lakekeeper:8181/catalog")
        .config(f"spark.sql.catalog.{CATALOG}.warehouse", "demo")
        .config(f"spark.sql.catalog.{CATALOG}.header.X-Iceberg-Access-Delegation", "vended-credentials")
        .config("spark.sql.defaultCatalog", CATALOG).getOrCreate())
def ensure_namespaces(spark):
    for ns in ("bronze", "silver", "gold"):
        spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {CATALOG}.{ns}")
