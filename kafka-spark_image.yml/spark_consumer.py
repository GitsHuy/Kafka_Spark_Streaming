import json
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

# Hàm để xử lý và tính tổng số tiền trong mỗi RDD
def process_rdd(rdd):
    if not rdd.isEmpty():
        total_amount = rdd.map(lambda record: json.loads(record[1])) \
                          .map(lambda data: data.get('so_tien', 0)) \
                          .reduce(lambda a, b: a + b)

        print("-------------------------------------------")
        print(f"Tổng số tiền trong batch này: {total_amount:,} VND")
        print("-------------------------------------------")

# Cấu hình Spark
sc = SparkContext(appName="KafkaSparkStreamingDemo")
sc.setLogLevel("WARN") # Giảm bớt log thừa cho dễ nhìn

# Tạo StreamingContext với batch interval là 5 giây
ssc = StreamingContext(sc, 5)

# Thông số kết nối Kafka
# Lưu ý: Vì Spark chạy trong Docker network, nó sẽ kết nối tới Kafka
# qua tên service 'kafka' và port 9092.
kafka_params = {
    "bootstrap.servers": "kafka:9092",
    "group.id": "spark-streaming-group" # Định danh consumer group
}
topic = "giao_dich"

# Tạo Direct Stream từ Kafka
# Đây chính là cách sử dụng KafkaUtils.createDirectStream
kafka_stream = KafkaUtils.createDirectStream(
    ssc, 
    [topic], 
    kafka_params
)

# Xử lý mỗi RDD trong DStream
kafka_stream.foreachRDD(process_rdd)

# Bắt đầu xử lý
ssc.start()
ssc.awaitTermination()