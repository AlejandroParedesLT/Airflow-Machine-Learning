import os
import logging
from confluent_kafka import Consumer, KafkaException, KafkaError
from ..models import Estado_ATM as atm

log_file = './mlapi_logs.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TopicConsumer_ATM:
    def __init__(self):
        self.consumer_config = {
            'bootstrap.servers': os.environ["KAFKA_BOOTSTRAP_SERVERS"],
            'group.id': os.environ["KAFKA_GROUP_TRANZAXIS"],
            'auto.offset.reset': os.environ["AUTO_OFFSET_RESET"]
        }
        self.consumer = Consumer(self.consumer_config)
        self.topic = os.environ["KAFKA_TOPIC_01_TRANZAXIS"]

    async def process_messages(self):
        while True:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logging.info(f"TopicConsumer_ATM.start - Error - End of partition: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                logging.info(f"TopicConsumer_ATM.start - Info - Received message: {msg.value().decode('utf-8')}")
                await atm.process_message(msg.value().decode('utf-8'))

    async def start(self):
        self.consumer.subscribe([self.topic])
        try:
            logging.info("Inicio de la clase consumer_estado_ATM")
            await self.process_messages()
        except Exception as e:
            logging.error(f"TopicConsumer_ATM.start - Error in Kafka consumer: {e}")
        finally:
            self.consumer.close()
