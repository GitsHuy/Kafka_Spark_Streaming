# Kafka-Spark Streaming Demo

Dự án hướng dẫn xây dựng pipeline xử lý dữ liệu thời gian thực với Kafka và Spark Streaming trên hai môi trường: Ubuntu Server (cài đặt thủ công) và Docker (sử dụng Docker Compose). Pipeline bao gồm Kafka producer gửi dữ liệu giao dịch vào topic và Spark consumer xử lý để tính tổng số tiền giao dịch theo thời gian thực.

## Yêu cầu
- **Ubuntu Server (cài đặt thủ công):**
  - Java (OpenJDK 8 hoặc 11)
  - Apache Kafka 3.7.2
  - Apache Spark 3.5.3
  - Python 3.x và `kafka-python` (`pip install kafka-python`)
- **Docker (Docker Compose):**
  - Docker và Docker Compose
  - Python 3.x và `kafka-python` (`pip install kafka-python`)

## Cấu trúc dự án
- **Chung:**
  - `producer.py`: Gửi dữ liệu giao dịch vào Kafka
  - `spark_consumer.py` (Docker) / `spark_streaming.py` (Ubuntu): Xử lý dữ liệu từ Kafka
- **Ubuntu:**
  - `kafka_folder/`: Thư mục chứa Kafka
  - `transactions.csv`: Dữ liệu mẫu
- **Docker:**
  - `docker-compose.yml`: Cấu hình Kafka và Spark

## Thiết lập và chạy chương trình

### Phần 1: Cài đặt trên Ubuntu Server

#### Bước 1: Cài đặt Kafka
1. Tải và giải nén Kafka:
```bash
cd /home/hadoopnhutvinh
wget https://downloads.apache.org/kafka/3.7.2/kafka_2.13-3.7.2.tgz
tar -xzf kafka_2.13-3.7.2.tgz
mv kafka_2.13-3.7.2 kafka_folder
```
2. Nếu đã cài Hive, sao lưu file xung đột:
```bash
mv /home/hadoopnhutvinh/hive/lib/kafka-clients-2.5.0.jar /home/hadoopnhutvinh/hive/lib/kafka-clients-2.5.0.jar.bak
mv /home/hadoopnhutvinh/hive/lib/zookeeper-3.8.3.jar /home/hadoopnhutvinh/hive/lib/zookeeper-3.8.3.jar.bak
mv /home/hadoopnhutvinh/hive/lib/zookeeper-jute-3.8.3.jar /home/hadoopnhutvinh/hive/lib/zookeeper-jute-3.8.3.jar.bak
```

#### Bước 2: Cấu hình Kafka
1. Chỉnh sửa `/home/hadoopnhutvinh/kafka_folder/config/server.properties`:
```bash
broker.id=1
listeners=PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://192.168.x.x:9092
zookeeper.connect=192.168.x.x:2181
```
2. Chỉnh sửa `/home/hadoopnhutvinh/kafka_folder/config/zookeeper.properties`:
```bash
dataDir=/home/hadoopnhutvinh/zookeeper/data
clientPort=2181
maxClientCnxns=0
```

#### Bước 3: Khởi động Zookeeper và Kafka
```bash
/home/hadoopnhutvinh/kafka_folder/bin/zookeeper-server-start.sh -daemon /home/hadoopnhutvinh/kafka_folder/config/zookeeper.properties
/home/hadoopnhutvinh/kafka_folder/bin/kafka-server-start.sh -daemon /home/hadoopnhutvinh/kafka_folder/config/server.properties
```
Kiểm tra dịch vụ:
```bash
jps
```
Xác nhận thấy `Kafka` và `QuorumPeerMain` (Zookeeper).

#### Bước 4: Tạo Kafka Topic
Tạo topic `transactions`:
```bash
/home/hadoopnhutvinh/kafka_folder/bin/kafka-topics.sh --create --topic transactions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

#### Bước 5: Chuẩn bị môi trường Python
1. Tạo và kích hoạt môi trường ảo:
```bash
python3 -m venv ~/myenv
source ~/myenv/bin/activate
```
2. Cài đặt `kafka-python`:
```bash
pip install kafka-python
```

#### Bước 6: Tạo dữ liệu mẫu
Lưu file `transactions.csv`:
```bash
nano transactions.csv
```
Nội dung:
```
id,amount,location
T001,1000,HoChiMinh
T002,2500,Hanoi
T003,1500,Danang
T004,2000,CanTho
T005,3000,Haiphong
T006,1800,QuangNinh
T007,2700,NhaTrang
T008,3500,Hue
T009,2200,HoChiMinh
T010,2600,Hanoi
```

#### Bước 7: Chạy Producer
Chạy script `producer.py`:
```bash
python3 producer.py
```

#### Bước 8: Chạy Spark Streaming
Chạy script `spark_streaming.py`:
```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3,org.apache.spark:spark-token-provider-kafka-0-10_2.12:3.5.3 spark_streaming.py
```

#### Bước 9: Kiểm tra kết quả
1. Kiểm tra dữ liệu trong topic:
```bash
/home/hadoopnhutvinh/kafka_folder/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic transactions --from-beginning
```
2. Kiểm tra danh sách topic:
```bash
cd /home/hadoopnhutvinh/kafka_folder/bin
./kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Phần 2: Cài đặt trên Docker

#### Bước 1: Khởi động dịch vụ
Chạy lệnh để khởi động Kafka và Spark:
```bash
docker-compose up -d
```

#### Bước 2: Tạo Kafka Topic
1. Truy cập container Kafka:
```bash
docker exec -it kafka /bin/bash
```
2. Tạo topic `giao_dich`:
```bash
kafka-topics.sh --create --topic giao_dich --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1
```
3. Thoát container:
```bash
exit
```

#### Bước 3: Chạy Producer
1. Cài đặt `kafka-python`:
```bash
pip install kafka-python
```
2. Chạy script `producer.py`:
```bash
python producer.py
```

#### Bước 4: Chạy Spark Consumer
1. Sao chép script `spark_consumer.py` vào container:
```bash
docker cp spark_consumer.py spark-master:/opt/bitnami/spark/
```
2. Chạy consumer:
```bash
docker exec spark-master /opt/bitnami/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 /opt/bitnami/spark/spark_consumer.py
```

## Kết quả mong đợi
- **Ubuntu:** Producer gửi dữ liệu từ `transactions.csv` vào topic `transactions`. Spark Streaming xử lý và in tổng số tiền giao dịch theo địa điểm.
- **Docker:** Producer gửi dữ liệu giao dịch (ví dụ: `{'id': 1, 'so_tien': 123456, 'dia_diem': 'Ha Noi'}`) vào topic `giao_dich`. Consumer xử lý mỗi 5 giây và in tổng số tiền (ví dụ: `Tổng số tiền trong batch này: 1,234,567 VND`).

## Lưu ý
- **Ubuntu:** Đảm bảo phiên bản Spark (3.5.3) khớp với gói `--packages`. Thay `192.168.x.x` bằng IP máy bạn.
- **Docker:** Đảm bảo phiên bản Spark (`bitnami/spark:3.3`) khớp với gói `--packages` (`spark-sql-kafka-0-10_2.12:3.3.0`).
- Dừng dịch vụ:
  - Ubuntu: Dừng Kafka/Zookeeper bằng `Ctrl+C` hoặc kill process.
  - Docker: `docker-compose down`

## Khắc phục sự cố
- **Ubuntu:**
  - Kiểm tra dịch vụ bằng `jps`.
  - Xem log: `tail -f /home/hadoopnhutvinh/kafka_folder/logs/server.log`.
  - Đảm bảo `kafka.bootstrap.servers` (`localhost:9092`) đúng trong `spark_streaming.py`.
- **Docker:**
  - Kiểm tra `bootstrap.servers` (`kafka:9092`) trong `spark_consumer.py`.
  - Xem log: `docker logs kafka` hoặc `docker logs spark-master`.
