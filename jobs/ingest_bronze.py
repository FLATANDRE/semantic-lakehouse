from pyspark.sql import functions as F, types as T
from common import ensure_namespaces, spark_session
spark = spark_session("bronze-ingestion"); ensure_namespaces(spark)
base = "/opt/lakehouse/data/raw"
schemas = {
 "customers": T.StructType([T.StructField("customer_id",T.StringType(),False),T.StructField("name",T.StringType(),False),T.StructField("email",T.StringType(),False),T.StructField("country",T.StringType(),False),T.StructField("created_at",T.DateType(),False)]),
 "products": T.StructType([T.StructField("product_id",T.StringType(),False),T.StructField("name",T.StringType(),False),T.StructField("category_code",T.StringType(),False),T.StructField("unit_price",T.DecimalType(12,2),False)]),
 "orders": T.StructType([T.StructField("order_id",T.StringType(),False),T.StructField("customer_id",T.StringType(),False),T.StructField("product_id",T.StringType(),False),T.StructField("quantity",T.IntegerType(),False),T.StructField("order_ts",T.TimestampType(),False)])}
for table, schema in schemas.items():
    df=(spark.read.option("header",True).option("timestampFormat","yyyy-MM-dd'T'HH:mm:ssX").schema(schema).csv(f"{base}/{table}.csv").withColumn("_ingested_at",F.current_timestamp()).withColumn("_source_file",F.input_file_name()))
    df.writeTo(f"lakehouse.bronze.{table}").using("iceberg").tableProperty("format-version","2").createOrReplace()
spark.stop()
