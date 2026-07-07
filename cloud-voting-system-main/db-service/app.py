from flask import Flask, request, jsonify
import sqlite3, os, time

app = Flask(__name__)
DB_PATH = '/app/votes.db'

VOTERS = {
    'ABC1234567': {'name': 'Rajesh Kumar', 'constituency': 'Chennai',  'mobile': '9876543210'},
    'DEF2345678': {'name': 'Priya Sharma', 'constituency': 'Chennai',  'mobile': '9876543211'},
    'GHI3456789': {'name': 'Suresh Babu',  'constituency': 'Chennai',  'mobile': '9876543212'},
    'JKL4567890': {'name': 'Meena Devi',   'constituency': 'Mumbai',   'mobile': '9876543213'},
    'MNO5678901': {'name': 'Arjun Patel',  'constituency': 'Mumbai',   'mobile': '9876543214'},
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_id TEXT NOT NULL,
        candidate_id TEXT NOT NULL,
        constituency TEXT NOT NULL DEFAULT '',
        timestamp REAL NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS voters (
        voter_id TEXT PRIMARY KEY,
        name TEXT, constituency TEXT,
        has_voted INTEGER DEFAULT 0)''')
    for vid, info in VOTERS.items():
        c.execute('INSERT OR IGNORE INTO voters VALUES (?,?,?,0)',
                  (vid, info['name'], info['constituency']))
    conn.commit()
    conn.close()

@app.route('/api/voter/<voter_id>', methods=['GET'])
def get_voter(voter_id):
    voter_info = VOTERS.get(voter_id.upper())
    if not voter_info:
        return jsonify({'found': False})
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT has_voted FROM voters WHERE voter_id=?', (voter_id.upper(),))
    row = c.fetchone()
    conn.close()
    has_voted = bool(row[0]) if row else False
    return jsonify({
        'found': True,
        'name': voter_info['name'],
        'constituency': voter_info['constituency'],
        'mobile': voter_info['mobile'],
        'has_voted': has_voted
    })

@app.route('/api/voter/<voter_id>/voted', methods=['POST'])
def mark_voted(voter_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('UPDATE voters SET has_voted=1 WHERE voter_id=?', (voter_id.upper(),))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/vote', methods=['POST'])
def record_vote():
    d = request.json
    conn = sqlite3.connect(DB_PATH)
    conn.execute('INSERT INTO votes (voter_id,candidate_id,constituency,timestamp) VALUES (?,?,?,?)',
        (d['voter_id'], d['candidate_id'],
         d.get('constituency', ''), d.get('timestamp', time.time())))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/results', methods=['GET'])
def results():
    constituency = request.args.get('constituency', '')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if constituency:
        c.execute('SELECT candidate_id,COUNT(*) FROM votes WHERE constituency=? GROUP BY candidate_id ORDER BY 2 DESC', (constituency,))
    else:
        c.execute('SELECT candidate_id,COUNT(*) FROM votes GROUP BY candidate_id ORDER BY 2 DESC')
    rows = c.fetchall()
    total = sum(r[1] for r in rows)
    conn.close()
    return jsonify({'total_votes': total, 'results': [
        {'candidate_id': r[0], 'votes': r[1],
         'percentage': round(r[1]/total*100,1) if total else 0} for r in rows]})

@app.route('/api/voters', methods=['GET'])
def all_voters():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('SELECT voter_id,name,constituency,has_voted FROM voters').fetchall()
    conn.close()
    return jsonify([{'voter_id':r[0],'name':r[1],'constituency':r[2],
                     'has_voted':bool(r[3])} for r in rows])

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=6000, debug=True)
