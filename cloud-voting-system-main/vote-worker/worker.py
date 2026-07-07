import os, json, time, socket, requests, pika

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
DB_URL        = os.getenv('DB_URL', 'http://db-service:6000')
EXCHANGE      = 'events'
QUEUE_NAME    = os.getenv('QUEUE_NAME', 'votes')
BINDING_KEYS  = ['vote.cast']
INSTANCE_ID   = socket.gethostname()

def connect():
    while True:
        try:
            conn = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=30))
            print(f'[worker:{INSTANCE_ID}] Connected to RabbitMQ', flush=True)
            return conn
        except Exception as e:
            print(f'[worker:{INSTANCE_ID}] RabbitMQ not ready: {e}. Retrying...', flush=True)
            time.sleep(2)

def publish_count_update(ch, voter_id, candidate_id, constituency):
    """After saving a vote, publish a vote.counted event so result-service updates live count."""
    try:
        # Get latest totals from DB
        resp  = requests.get(f'{DB_URL}/api/results', timeout=3)
        totals = resp.json()
        event = {
            'event':        'vote.counted',
            'voter_id':     voter_id,
            'candidate_id': candidate_id,
            'constituency': constituency,
            'total_votes':  totals.get('total_votes', 0),
            'timestamp':    time.time(),
            'worker':       INSTANCE_ID,
        }
        ch.basic_publish(
            exchange=EXCHANGE,
            routing_key='vote.counted',
            body=json.dumps(event).encode(),
            properties=pika.BasicProperties(delivery_mode=2))
        print(f'[worker:{INSTANCE_ID}] 📊 Published vote.counted — total: {totals.get("total_votes",0)}', flush=True)
    except Exception as e:
        print(f'[worker:{INSTANCE_ID}] ⚠️  Could not publish count update: {e}', flush=True)

def on_message(ch, method, properties, body):
    event        = json.loads(body.decode('utf-8'))
    voter_id     = event.get('voter_id')
    candidate_id = event.get('candidate_id')
    constituency = event.get('constituency', '')
    print(f'[worker:{INSTANCE_ID}] ✅ Vote DEQUEUED: {voter_id} -> {candidate_id} ({constituency})', flush=True)
    time.sleep(3)  # Intentional delay so RabbitMQ queue depth is visible in management UI
    try:
        requests.post(f'{DB_URL}/api/vote',
            json={'voter_id': voter_id, 'candidate_id': candidate_id,
                  'constituency': constituency, 'timestamp': event.get('timestamp')},
            timeout=3)
        print(f'[worker:{INSTANCE_ID}] ✅ Vote COMMITTED to database for voter: {voter_id}', flush=True)
        # Publish count update so live results reflect immediately
        publish_count_update(ch, voter_id, candidate_id, constituency)
        print(f'[worker:{INSTANCE_ID}] 📨 Message ACKed — removed from RabbitMQ queue.', flush=True)
    except Exception as e:
        print(f'[worker:{INSTANCE_ID}] ❌ DB error — vote NOT saved: {e}', flush=True)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    conn = connect()
    ch   = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)
    # Votes queue
    ch.queue_declare(queue=QUEUE_NAME, durable=True)
    for key in BINDING_KEYS:
        ch.queue_bind(exchange=EXCHANGE, queue=QUEUE_NAME, routing_key=key)
    # Also declare the vote-counts queue so result-service can consume it
    ch.queue_declare(queue='vote-counts', durable=True)
    ch.queue_bind(exchange=EXCHANGE, queue='vote-counts', routing_key='vote.counted')
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)
    print(f'[worker:{INSTANCE_ID}] Waiting for votes on queue={QUEUE_NAME}...', flush=True)
    ch.start_consuming()

if __name__ == '__main__':
    main()