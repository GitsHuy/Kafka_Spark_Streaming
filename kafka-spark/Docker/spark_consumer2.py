import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, sum
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType

# Khởi tạo SparkSession, entry point mới cho Spark 2.x trở lên
spark = SparkSession \
    .builder \
    .appName("KafkaSparkStructuredStreamingDemo") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Đọc dữ liệu từ Kafka dưới dạng một DataFrame streaming
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "giao_dich") \
    .load()

# Định nghĩa cấu trúc (schema) của dữ liệu JSON trong message
schema = StructType([
    StructField("id", IntegerType()),
    StructField("so_tien", LongType()),
    StructField("dia_diem", StringType()),
])

# Xử lý DataFrame
# 1. Chuyển cột 'value' từ dạng binary sang string
# 2. Parse chuỗi JSON thành các cột riêng biệt dựa trên schema
# 3. Gom nhóm và tính tổng cột "so_tien"
result_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.so_tien") \
    .agg(sum("so_tien").alias("total_amount"))

# Xuất kết quả ra console
query = result_df \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()