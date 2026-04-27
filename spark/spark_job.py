from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    explode_outer,
    size,
    sum as fsum,
    avg as favg,
    count as fcount,
)

spark = (
    SparkSession.builder.appName("EcommerceKPIs")
    .master("local[*]")
    .config("spark.es.nodes", "elasticsearch")
    .config("spark.es.port", "9200")
    .config("spark.es.nodes.wan.only", "true")
    .getOrCreate()
)

# Read indices
products = (
    spark.read.format("org.elasticsearch.spark.sql")
    .option("es.resource", "ecommerce-products")
    .load()
)

orders = (
    spark.read.format("org.elasticsearch.spark.sql")
    .option("es.resource", "ecommerce-orders")
    .load()
)

# --- KPI 1 + 2 ---
total_products = products.count()
total_orders = orders.count()

# --- KPI 3 ---
avg_items_df = orders.agg(
    favg(col("total_items").cast("double")).alias("avg_items_per_order")
)

# --- Build order lines safely  ---
lines = (
    orders.select(explode_outer(col("products")).alias("line"))
    .where(col("line").isNotNull())
    .select(
        col("line.productId").cast("int").alias("productId"),
        col("line.quantity").cast("int").alias("quantity"),
    )
    .where(col("productId").isNotNull() & col("quantity").isNotNull())
)


orders_with_products = orders.where(size(col("products")) > 0).count()
lines_count = lines.count()
print(
    f"orders={total_orders} orders_with_products={orders_with_products} lines={lines_count}"
)

# --- KPI 4 ---
top_products_df = (
    lines.groupBy("productId")
    .agg(fsum("quantity").alias("total_qty"))
    .orderBy(col("total_qty").desc())
    .limit(10)
)

# --- KPI 5 ---
prod_sel = products.select(
    col("id").cast("int").alias("productId"),
    col("category"),
    col("price").cast("double").alias("price"),
)

revenue_by_category_df = (
    lines.join(prod_sel, on="productId", how="left")
    .where(col("price").isNotNull() & col("category").isNotNull())
    .withColumn("line_revenue", col("quantity") * col("price"))
    .groupBy("category")
    .agg(
        fsum("line_revenue").alias("estimated_revenue"),
        fsum("quantity").alias("total_qty"),
        fcount("*").alias("lines"),
    )
    .orderBy(col("estimated_revenue").desc())
)

# --- Save ALL KPIs ---
# totals as a 1-row csv
spark.createDataFrame(
    [(int(total_products), int(total_orders))], ["total_products", "total_orders"]
).coalesce(1).write.mode("overwrite").option("header", True).csv("/data/totals")

avg_items_df.coalesce(1).write.mode("overwrite").option("header", True).csv(
    "/data/avg_items_per_order"
)
top_products_df.coalesce(1).write.mode("overwrite").option("header", True).csv(
    "/data/top_products"
)
revenue_by_category_df.coalesce(1).write.mode("overwrite").option("header", True).csv(
    "/data/revenue_by_category"
)

# small summary text
avg_val = avg_items_df.collect()[0]["avg_items_per_order"]
with open("/data/summary.txt", "w") as f:
    f.write(f"total_products={total_products}\n")
    f.write(f"total_orders={total_orders}\n")
    f.write(f"avg_items_per_order={avg_val}\n")
    f.write(f"orders_with_products={orders_with_products}\n")
    f.write(f"lines={lines_count}\n")

spark.stop()
