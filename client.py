import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel_out = connection.channel()

channel_out.queue_declare(queue='in')

channel_in = connection.channel()
channel_in.queue_declare(queue='out')
channel_in.exchange_declare(exchange='out', type='fanout')

result = channel_in.queue_declare(exclusive=True)
queue_name = result.method.queue

channel_in.queue_bind(exchange='out', queue=queue_name)

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    return "Ilus Annika on super ilus."

channel_in.basic_consume(callback,
                         queue=queue_name,
                         no_ack=True)

#print(' [*] Waiting for messages. To exit press CTRL+C')

channel_out.basic_publish(exchange='',
                      routing_key='in',
                      body='Client 2!')
print(" [x] Sent 'Client 2!'")

a = channel_in.start_consuming()
print a
#connection.close()
