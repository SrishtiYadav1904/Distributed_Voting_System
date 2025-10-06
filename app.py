#!/usr/bin/env python3
"""
Flask-based Distributed Voting System
Simplified version with admin controls and real-time notifications
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import threading
import time
from datetime import datetime
from collections import deque
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'voting_system_secret_key_2024'

# Global voting state
voting_active = False
results_published = False
current_voting_session = 1

# In-memory storage
VOTERS_DB = [
    {"id": 1, "name": "Alice", "has_voted": False, "vote": None},
    {"id": 2, "name": "Bob", "has_voted": False, "vote": None},
    {"id": 3, "name": "Charlie", "has_voted": False, "vote": None},
    {"id": 4, "name": "Diana", "has_voted": False, "vote": None},
    {"id": 5, "name": "Eve", "has_voted": False, "vote": None},
    {"id": 6, "name": "Frank", "has_voted": False, "vote": None},
    {"id": 7, "name": "Grace", "has_voted": False, "vote": None},
    {"id": 8, "name": "Henry", "has_voted": False, "vote": None},
    {"id": 9, "name": "Ivy", "has_voted": False, "vote": None},
    {"id": 10, "name": "Jack", "has_voted": False, "vote": None}
]

CANDIDATES = [
    "Candidate A", "Candidate B", "Candidate C", "Candidate D", "Candidate E",
    "Candidate F", "Candidate G", "Candidate H", "Candidate I", "Candidate J"
]

# Tally server data
VOTES = {}  # Real-time vote tracking: {candidate: count}
VOTED_USERS = set()  # Track who has voted to prevent re-voting

# Voting history - stores all past voting sessions
VOTING_HISTORY = []  # List of completed voting sessions

# System notifications
NOTIFICATIONS = deque(maxlen=50)
notification_lock = threading.Lock()

# Initialize vote counts
for candidate in CANDIDATES:
    VOTES[candidate] = 0

def add_notification(message):
    """Add a notification to the system log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    notification = f"[{timestamp}] {message}"
    
    with notification_lock:
        NOTIFICATIONS.append(notification)
        logger.info(f"Notification: {message}")

def get_voter_by_credentials(name, voter_id):
    """Find voter by name and ID"""
    for voter in VOTERS_DB:
        if voter["name"] == name and voter["id"] == voter_id:
            return voter
    return None

def update_vote_count(candidate):
    """Update real-time vote count"""
    if candidate in VOTES:
        VOTES[candidate] += 1

def save_current_session_to_history():
    """Save current voting session to history"""
    global current_voting_session
    
    # Calculate winner
    winner = None
    max_votes = 0
    for candidate, votes in VOTES.items():
        if votes > max_votes:
            max_votes = votes
            winner = candidate
    
    # Create session record
    session_record = {
        "session_id": current_voting_session,
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "votes": VOTES.copy(),
        "winner": winner,
        "total_votes": sum(VOTES.values()),
        "participants": list(VOTED_USERS.copy()),
        "voter_details": []
    }
    
    # Add voter details
    for voter in VOTERS_DB:
        if voter["has_voted"]:
            session_record["voter_details"].append({
                "id": voter["id"],
                "name": voter["name"],
                "vote": voter["vote"]
            })
    
    VOTING_HISTORY.append(session_record)
    add_notification(f"Session {current_voting_session} saved to history with {session_record['total_votes']} votes")

def reset_current_session():
    """Reset current voting session for new voting"""
    global voting_active, results_published, current_voting_session
    
    # Reset voting state
    voting_active = False
    results_published = False
    current_voting_session += 1
    
    # Reset voter database
    for voter in VOTERS_DB:
        voter["has_voted"] = False
        voter["vote"] = None
    
    # Reset vote counts
    for candidate in CANDIDATES:
        VOTES[candidate] = 0
    
    # Clear voted users
    VOTED_USERS.clear()
    
    add_notification(f"New voting session {current_voting_session} initialized")

# Routes

@app.route('/')
def index():
    """Main voting interface"""
    if 'logged_in' not in session:
        return render_template('login.html')
    
    # Check if user has already voted
    user_name = session.get('name')
    if user_name in VOTED_USERS:
        return render_template('voted.html', 
                             message="You have already voted. Result will be notified soon.")
    
    # Check if voting is active
    if not voting_active:
        return render_template('voting_inactive.html')
    
    return render_template('vote.html', candidates=CANDIDATES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        try:
            voter_id = int(request.form.get('voter_id', 0))
        except ValueError:
            flash('Invalid voter ID')
            return render_template('login.html')
        
        voter = get_voter_by_credentials(name, voter_id)
        if voter:
            session['logged_in'] = True
            session['name'] = name
            session['voter_id'] = voter_id
            
            add_notification(f"{name} logged in")
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    if 'name' in session:
        add_notification(f"{session['name']} logged out")
    
    session.clear()
    return redirect(url_for('index'))

@app.route('/vote', methods=['POST'])
def vote():
    """Handle vote submission"""
    if 'logged_in' not in session:
        return jsonify({"success": False, "message": "Not logged in"})
    
    if not voting_active:
        return jsonify({"success": False, "message": "Voting is not active"})
    
    user_name = session.get('name')
    
    # Check if user has already voted
    if user_name in VOTED_USERS:
        return jsonify({"success": False, "message": "You have already voted. Result will be notified soon."})
    
    candidate = request.json.get('candidate')
    if candidate not in CANDIDATES:
        return jsonify({"success": False, "message": "Invalid candidate"})
    
    # Record the vote
    voter_id = session.get('voter_id')
    for voter in VOTERS_DB:
        if voter['id'] == voter_id:
            voter['has_voted'] = True
            voter['vote'] = candidate
            break
    
    # Add to voted users set
    VOTED_USERS.add(user_name)
    
    # Update real-time vote count
    update_vote_count(candidate)
    
    # Add notification
    add_notification(f"{user_name} voted")
    
    return jsonify({"success": True, "message": "Vote recorded successfully"})

@app.route('/admin')
def admin():
    """Admin dashboard"""
    return render_template('admin.html', 
                         voting_active=voting_active,
                         results_published=results_published,
                         voters=VOTERS_DB,
                         votes=VOTES,
                         notifications=list(NOTIFICATIONS),
                         current_session=current_voting_session)

@app.route('/admin/start_voting', methods=['POST'])
def start_voting():
    """Start voting"""
    global voting_active, results_published
    voting_active = True
    results_published = False
    
    add_notification("Voting started")
    return jsonify({"success": True, "message": "Voting started"})

@app.route('/admin/stop_voting', methods=['POST'])
def stop_voting():
    """Stop voting"""
    global voting_active
    voting_active = False
    
    add_notification("Voting stopped")
    return jsonify({"success": True, "message": "Voting stopped"})

@app.route('/admin/publish_results', methods=['POST'])
def publish_results():
    """Publish results"""
    global results_published
    
    if voting_active:
        return jsonify({"success": False, "message": "Cannot publish results while voting is active"})
    
    results_published = True
    
    # Find winner
    winner = max(VOTES.items(), key=lambda x: x[1]) if VOTES else None
    winner_msg = f"Winner: {winner[0]} with {winner[1]} votes" if winner and winner[1] > 0 else "No votes cast"
    
    add_notification(f"Results published - {winner_msg}")
    return jsonify({"success": True, "message": "Results published successfully"})

@app.route('/admin/start_new_voting', methods=['POST'])
def start_new_voting():
    """Start a new voting session (saves current to history and resets)"""
    global voting_active, results_published
    
    if voting_active:
        return jsonify({"success": False, "message": "Cannot start new voting while current session is active"})
    
    # Save current session to history if there were any votes
    if sum(VOTES.values()) > 0 or results_published:
        save_current_session_to_history()
    
    # Reset for new session
    reset_current_session()
    
    return jsonify({"success": True, "message": f"New voting session {current_voting_session} started"})

@app.route('/admin/history')
def voting_history():
    """View voting history"""
    return render_template('voting_history.html', 
                         history=VOTING_HISTORY,
                         current_session=current_voting_session)

@app.route('/api/notifications')
def api_notifications():
    """API endpoint for live notifications"""
    return jsonify({"notifications": list(NOTIFICATIONS)})

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify({
        "voting_active": voting_active,
        "results_published": results_published,
        "total_votes": sum(VOTES.values()),
        "voted_users": len(VOTED_USERS)
    })

@app.route('/results')
def results():
    """Show results page"""
    if not results_published:
        return render_template('results_pending.html')
    
    # Calculate winner
    winner = None
    max_votes = 0
    for candidate, votes in VOTES.items():
        if votes > max_votes:
            max_votes = votes
            winner = candidate
    
    return render_template('results.html', 
                         votes=VOTES, 
                         winner=winner, 
                         total_votes=sum(VOTES.values()))

if __name__ == '__main__':
    print("Flask Voting System starting...")
    print("Access points:")
    print("- Main interface: http://localhost:5000")
    print("- Admin dashboard: http://localhost:5000/admin")
    print("- Results: http://localhost:5000/results")
    
    app.run(debug=True, host='localhost', port=5000)
