from flask import Flask, render_template
import requests, os
app = Flask(__name__)
DB_URL = os.getenv('DB_URL', 'http://db-service:6000')
@app.route('/')
def admin():
    try:
        voters = requests.get(f'{DB_URL}/api/voters', timeout=3).json()
        results = requests.get(f'{DB_URL}/api/results', timeout=3).json()
    except:
        voters, results = [], {'total_votes': 0, 'results': []}
    return render_template('admin.html', voters=voters, results=results)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
