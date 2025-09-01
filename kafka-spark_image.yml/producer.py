import json
import time
import random
from kafka import KafkaProducer

# Tạo một producer kết nối đến Kafka server
# Lưu ý: Vì script này chạy từ máy thật của bạn (bên ngoài Docker), 
# chúng ta sẽ kết nối tới port 9093 đã được map ra localhost.
producer = KafkaProducer(
    bootstrap_servers=['localhost:9093'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic_name = 'giao_dich'
print(f"Bắt đầu gửi dữ liệu tới topic '{topic_name}'...")

# Vòng lặp vô hạn để gửi dữ liệu
transaction_id = 1
while True:
    try:
        # Tạo dữ liệu giao dịch giả
        data = {
            'id': transaction_id,
            'so_tien': random.randint(10000, 5000000), # Số tiền ngẫu nhiên từ 10k đến 5m
            'dia_diem': random.choice(['Ha Noi', 'Ho Chi Minh', 'Da Nang', 'Can Tho'])
        }

        # Gửi message tới Kafka
        producer.send(topic_name, value=data)
        print(f"Đã gửi: {data}")

        transaction_id += 1
        time.sleep(1) # Tạm dừng 1 giây

    except KeyboardInterrupt:
        print("\nĐã dừng producer.")
        break
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
        break

# Đảm bảo tất cả message đã được gửi đi trước khi thoát
producer.flush()
producer.close()