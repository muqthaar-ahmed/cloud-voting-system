from flask import Flask, render_template
import requests, os

app = Flask(__name__)
DB_URL = os.getenv('DB_URL', 'http://db-service:6000')

CANDIDATE_NAMES = {
    'CAND_001': {'name': 'Karthik Rajan',      'party': 'INC', 'color': '#00bcd4'},
    'CAND_002': {'name': 'Vijay Annamalai',    'party': 'BJP', 'color': '#ff9800'},
    'CAND_003': {'name': 'Lakshmi Prabhakaran','party': 'DMK', 'color': '#e53935'},
    'CAND_004': {'name': 'Murugan Selvam',     'party': 'AIADMK','color': '#43a047'},
}

@app.route('/')
def results():
    try:
        resp = requests.get(f'{DB_URL}/api/results', timeout=3)
        data = resp.json()
        for r in data.get('results', []):
            info = CANDIDATE_NAMES.get(r['candidate_id'], {})
            r['name'] = info.get('name', r['candidate_id'])
            r['party'] = info.get('party', '')
            r['color'] = info.get('color', '#64748b')
        return render_template('results.html', data=data)
    except Exception as e:
        return render_template('results.html', data={'total_votes':0,'results':[]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
