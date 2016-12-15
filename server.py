import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel_in = connection.channel()

channel_in.queue_declare(queue='in')

channel_out = connection.channel()

channel_out.queue_declare(queue='out')
channel_out.exchange_declare(exchange='out', type='fanout')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    channel_out.basic_publish(exchange='out', routing_key='', body='Got response')

channel_in.basic_consume(callback,
                      queue='in',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel_in.start_consuming()
