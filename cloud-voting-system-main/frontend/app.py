from flask import Flask, render_template, request, redirect, session, jsonify
import requests, os, random, time

app = Flask(__name__)
app.secret_key = 'cloudvote_secret_2025_secure'

VOTE_API = os.getenv('VOTE_API_URL', 'http://vote-api:5001')
DB_URL   = os.getenv('DB_URL', 'http://db-service:6000')

FIXED_STATE    = 'Tamil Nadu'
FIXED_DISTRICT = 'Chennai'

CANDIDATES = [
    {'id': 'CAND_001', 'name': 'Karthik Rajan',       'party': 'INC',    'color': '#00bcd4'},
    {'id': 'CAND_002', 'name': 'Vijay Annamalai',     'party': 'BJP',    'color': '#ff9800'},
    {'id': 'CAND_003', 'name': 'Lakshmi Prabhakaran', 'party': 'DMK',    'color': '#e53935'},
    {'id': 'CAND_004', 'name': 'Murugan Selvam',      'party': 'AIADMK', 'color': '#43a047'},
]

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    voter_id = request.form.get('voter_id', '').strip().upper()
    mobile   = request.form.get('mobile', '').strip()
    if not voter_id or not mobile:
        return jsonify({'success': False, 'message': 'Please enter both Voter ID and Mobile Number.'})
    try:
        resp  = requests.get(f'{DB_URL}/api/voter/{voter_id}', timeout=3)
        voter = resp.json()
    except:
        return jsonify({'success': False, 'message': 'Database unavailable. Try again.'})
    if not voter.get('found'):
        return jsonify({'success': False, 'message': 'Voter ID not found in database.'})
    if voter.get('has_voted'):
        return jsonify({'success': False, 'message': 'You have already cast your vote.'})
    if voter.get('mobile') != mobile:
        return jsonify({'success': False, 'message': 'Mobile number does not match our records.'})
    otp = str(random.randint(100000, 999999))
    session['otp']        = otp
    session['otp_time']   = time.time()
    session['voter_id']   = voter_id
    session['voter_name'] = voter.get('name', '')
    return jsonify({'success': True, 'otp': otp, 'name': voter.get('name', '')})

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    entered  = request.form.get('otp', '').strip()
    stored   = session.get('otp')
    otp_time = session.get('otp_time', 0)
    if not stored:
        return jsonify({'success': False, 'message': 'Session expired. Please start again.'})
    if time.time() - otp_time > 120:
        return jsonify({'success': False, 'message': 'OTP expired. Please request a new one.'})
    if entered != stored:
        return jsonify({'success': False, 'message': 'Incorrect OTP. Please try again.'})
    session['otp_verified'] = True
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    session['captcha_answer'] = str(a + b)
    return jsonify({'success': True, 'captcha_question': f'{a} + {b} = ?'})

@app.route('/verify-captcha', methods=['POST'])
def verify_captcha():
    if not session.get('otp_verified'):
        return jsonify({'success': False, 'message': 'Complete OTP step first.'})
    entered = request.form.get('captcha', '').strip()
    correct = session.get('captcha_answer', '')
    if entered != correct:
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        session['captcha_answer'] = str(a + b)
        return jsonify({'success': False, 'message': 'Wrong answer. Try the new question.',
                        'new_question': f'{a} + {b} = ?'})
    session['captcha_verified'] = True
    session['state']        = FIXED_STATE
    session['district']     = FIXED_DISTRICT
    session['location_set'] = True
    return jsonify({'success': True})

@app.route('/vote')
def vote():
    if not session.get('location_set'):
        return redirect('/')
    return render_template('vote.html',
        candidates=CANDIDATES,
        voter_id=session.get('voter_id', ''),
        voter_name=session.get('voter_name', ''),
        state=FIXED_STATE,
        district=FIXED_DISTRICT)

@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('location_set'):
        return redirect('/')
    voter_id       = request.form.get('voter_id', '').strip().upper()
    candidate_id   = request.form.get('candidate_id', '')
    candidate_name = request.form.get('candidate_name', '')
    try:
        resp = requests.post(f'{VOTE_API}/api/vote',
            json={'voter_id': voter_id, 'candidate_id': candidate_id,
                  'constituency': FIXED_DISTRICT}, timeout=5)
        data = resp.json()
        if data.get('success'):
            session.clear()
            return render_template('thankyou.html',
                candidate=candidate_name, district=FIXED_DISTRICT)
        return render_template('vote.html', candidates=CANDIDATES,
            voter_id=voter_id, voter_name=session.get('voter_name', ''),
            state=FIXED_STATE, district=FIXED_DISTRICT,
            error=data.get('message', 'Vote failed.'))
    except:
        return render_template('vote.html', candidates=CANDIDATES,
            voter_id=voter_id, voter_name=session.get('voter_name', ''),
            state=FIXED_STATE, district=FIXED_DISTRICT,
            error='Vote service unavailable. Please try again.')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)