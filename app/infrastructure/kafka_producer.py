import json

class KafkaJobProducer:
    def __init__(self):
        self.topic = "job_topic"

    async def push_job_payload(self, job_id: str, minio_url: str):
        # Đóng gói đúng cấu trúc Payload giống như bản vẽ thiết kế của đội bạn
        payload = {
            "job_id": job_id,
            "version": "1.0",
            "minio_url": minio_url,
            "tasks": ["line_detection", "ocr"]
        }
        print(f"[Kafka Broker] ⚡ [PUSH] Phát lệnh bài vào Topic '{self.topic}':")
        print(json.dumps(payload, indent=2))
        return True