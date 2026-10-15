from pyspark.sql import functions as F
from common import ensure_namespaces, spark_session
spark=spark_session("silver-quality"); ensure_namespaces(spark)
c=spark.table("lakehouse.bronze.customers"); p=spark.table("lakehouse.bronze.products"); o=spark.table("lakehouse.bronze.orders")
assert c.filter(F.col("customer_id").isNull()).count()==0
assert p.filter((F.col("unit_price")<=0)|F.col("category_code").isNull()).count()==0
assert o.filter(F.col("quantity")<=0).count()==0
frames={
 "customers": c.select("customer_id",F.initcap("name").alias("name"),F.lower(F.trim("email")).alias("email"),"country","created_at").dropDuplicates(["customer_id"]),
 "products": p.select("product_id",F.trim("name").alias("name"),F.upper(F.trim("category_code")).alias("category_code"),"unit_price"),
 "orders": o.select("order_id","customer_id","product_id","quantity","order_ts")}
for name,df in frames.items(): df.writeTo(f"lakehouse.silver.{name}").using("iceberg").tableProperty("format-version","2").createOrReplace()
spark.stop()
