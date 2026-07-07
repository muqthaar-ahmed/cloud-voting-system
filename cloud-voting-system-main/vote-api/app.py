from flask import Flask, request, jsonify
import pika, json, os, time, requests

app = Flask(__name__)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
DB_URL        = os.getenv('DB_URL', 'http://db-service:6000')
EXCHANGE      = 'events'

def get_rabbitmq_channel():
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=30))
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)
    return conn, ch

@app.route('/api/vote', methods=['POST'])
def cast_vote():
    data         = request.json
    voter_id     = data.get('voter_id', '').strip().upper()
    candidate_id = data.get('candidate_id', '').strip()
    constituency = data.get('constituency', '').strip()
    if not voter_id or not candidate_id:
        return jsonify({'success': False, 'message': 'Missing data.'}), 400
    try:
        resp  = requests.get(f'{DB_URL}/api/voter/{voter_id}', timeout=3)
        voter = resp.json()
    except:
        return jsonify({'success': False, 'message': 'DB unavailable.'}), 503
    if not voter.get('found'):
        return jsonify({'success': False, 'message': 'Voter ID not found.'}), 404
    if voter.get('has_voted'):
        return jsonify({'success': False, 'message': 'You have already voted.'}), 403
    try:
        conn, ch = get_rabbitmq_channel()
        event = {'voter_id': voter_id, 'candidate_id': candidate_id,
                 'constituency': constituency, 'timestamp': time.time()}
        ch.basic_publish(exchange=EXCHANGE, routing_key='vote.cast',
            body=json.dumps(event).encode(),
            properties=pika.BasicProperties(delivery_mode=2))
        conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': f'Queue error: {e}'}), 503
    # Mark voter as voted immediately
    try:
        requests.post(f'{DB_URL}/api/voter/{voter_id}/voted', timeout=3)
    except Exception as e:
        print(f'Warning: could not mark voter {voter_id} as voted: {e}')
    return jsonify({'success': True, 'message': 'Vote submitted!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
