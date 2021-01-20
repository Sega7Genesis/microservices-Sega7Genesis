import os
import pika
import json

Q_URL = os.environ.get('Q_URL', 'amqp://localhost')
Q_NAME = 'rabbit'

class Uses_Q:
    def connect(self):
        self.connection = pika.BlockingConnection(pika.URLParameters(Q_URL))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=Q_NAME)
        return self

    def disconnect(self):
        self.connection.close()

    def send(self, req):
        self.channel.basic_publish(routing_key='Q_NAME', body=json.dump(req))

    def take(self):
        for method_frame, properties, body in self.channel.consume(Q_NAME, inactivity_timeout=0):
            if not method_frame:
                break
            yield json.loads(body)
            self.channel.basic_ack(method_frame.delivery_tag)
