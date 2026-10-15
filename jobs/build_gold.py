from pyspark.sql import functions as F
from common import ensure_namespaces, spark_session
spark=spark_session("gold-ai-ready-features"); ensure_namespaces(spark)
c=spark.table("lakehouse.silver.customers").select("customer_id",F.col("name").alias("customer_name"),"country")
p=spark.table("lakehouse.silver.products").select("product_id",F.col("name").alias("product_name"),"category_code","unit_price")
o=spark.table("lakehouse.silver.orders")
features=(o.join(c,"customer_id").join(p,"product_id").withColumn("line_total",F.col("quantity")*F.col("unit_price")).groupBy("customer_id","customer_name","country","category_code").agg(F.countDistinct("order_id").alias("order_count"),F.sum("quantity").alias("units_bought"),F.sum("line_total").cast("decimal(14,2)").alias("gross_revenue"),F.max("order_ts").alias("last_order_ts")).withColumn("feature_generated_at",F.current_timestamp()))
features.writeTo("lakehouse.gold.customer_product_features").using("iceberg").tableProperty("format-version","2").createOrReplace()
spark.stop()
