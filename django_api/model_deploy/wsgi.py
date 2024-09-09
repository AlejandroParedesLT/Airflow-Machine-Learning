import os
import logging
import multiprocessing
import asyncio
from django.core.wsgi import get_wsgi_application
from .init_kafka import InitKafka
from django_api.api.kafka.controllers.consumer import TopicConsumer_ATM
from api.kafka.controllers.consumer_estado_atm2 import TopicConsumer_ATM2

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'model_deploy.settings')

application = get_wsgi_application()

log_file = './mlapi_logs.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def start_kafka_consumer(consumer_class):
    consumer = consumer_class()
    asyncio.run(consumer.start())  

async def main():
    init_kafka = InitKafka(
        bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"],
        topics=[
            os.environ["KAFKA_TOPIC_01_TRANZAXIS"],
            os.environ["KAFKA_TOPIC_02_TRANZAXIS"]
        ]
    )
    
    if await init_kafka.wait_for_topics():
        consumer_processes = [
            multiprocessing.Process(target=start_kafka_consumer, args=(TopicConsumer_ATM,)),
            multiprocessing.Process(target=start_kafka_consumer, args=(TopicConsumer_ATM2,))
        ]
        for process in consumer_processes:
            process.start()
        for process in consumer_processes:
            process.join()
    else:
        logging.error("Kafka cluster or topics are not available. Exiting.")

asyncio.run(main())
