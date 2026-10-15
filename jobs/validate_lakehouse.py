from common import spark_session
spark=spark_session("validate-lakehouse")
for table, minimum in {"bronze.customers":3,"bronze.products":4,"bronze.orders":5,"silver.customers":3,"silver.products":4,"silver.orders":5}.items():
    count=spark.table(f"lakehouse.{table}").count()
    assert count>=minimum, f"{table}: esperado >= {minimum}, obtido {count}"
assert spark.table("lakehouse.gold.customer_product_features").count()>0
assert spark.table("lakehouse.gold.semantic_entities").count()>0
spark.stop()
