#!/usr/bin/env python3
"""
Distributed Voting System - Client Dashboard
Web interface for voters to login, view candidates, and cast votes
"""

import time
import threading
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from xmlrpc.client import ServerProxy
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'voting_system_secret_key_2024'

# Server connections
VOTING_SERVER_URL = "http://localhost:8000"


def get_server_connection():
    """Get connection to voting server"""
    try:
        return ServerProxy(VOTING_SERVER_URL)
    except Exception as e:
        logger.error(f"Failed to connect to voting server: {e}")
        return None



@app.route('/')
def dashboard():
    """Main dashboard"""
    server = get_server_connection()

    
    candidates = []
    voting_status = None
    results = None
    user_has_voted = False
    deadline_str = None
    
    if server:
        try:
            # Get candidates
            candidates_response = server.GetOptions()
            if candidates_response.get('success'):
                candidates = candidates_response['candidates']
            
            # Get voting status
            voting_status = server.GetVotingStatus()
            
            # Check if user has voted
            if session.get('logged_in'):
                db_response = server.GetVoterDatabase()
                if db_response.get('success'):
                    for voter in db_response['voters']:
                        if (voter['id'] == session.get('voter_id') and 
                            voter['name'] == session.get('name')):
                            user_has_voted = voter['has_voted']
                            break
            
            # Format deadline
            if voting_status and voting_status.get('deadline'):
                deadline_str = datetime.fromtimestamp(voting_status['deadline']).strftime('%Y-%m-%d %H:%M:%S')
        
        except Exception as e:
            logger.error(f"Error getting server data: {e}")
    
    


@app.route('/register', methods=['POST'])
def register():
    """Register new voter"""
    name = request.form.get('name', '').strip()
    
    if not name:
        session['message'] = "Name is required"
        session['message_type'] = "error"
        return redirect(url_for('dashboard'))
    
    server = get_server_connection()
    if not server:
        session['message'] = "Cannot connect to voting server"
        session['message_type'] = "error"
        return redirect(url_for('dashboard'))
    
    try:
        result = server.Register(name)
        if result.get('success'):
            session['message'] = f"Registration successful! Your ID is: {result['id']}"
            session['message_type'] = "success"
        else:
            session['message'] = result.get('message', 'Registration failed')
            session['message_type'] = "error"
    except Exception as e:
        session['message'] = f"Registration error: {e}"
        session['message_type'] = "error"
    
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['POST'])
def login():
    """Login voter"""
    name = request.form.get('name', '').strip()
    voter_id = request.form.get('voter_id')
    
    if not name or not voter_id:
        session['message'] = "Name and Voter ID are required"
        session['message_type'] = "error"
        return redirect(url_for('dashboard'))
    
    try:
        voter_id = int(voter_id)
    except ValueError:
        session['message'] = "Voter ID must be a number"
        session['message_type'] = "error"
        return redirect(url_for('dashboard'))
    
    server = get_server_connection()
    if not server:
        session['message'] = "Cannot connect to voting server"
        session['message_type'] = "error"
        return redirect(url_for('dashboard'))
    
    try:
        result = server.Login(name, voter_id)
        if result.get('success'):
            session['logged_in'] = True
            session['name'] = name
            session['voter_id'] = voter_id
            session['session_id'] = result['session_id']
            session['message'] = "Login successful!"
            session['message_type'] = "success"
        else:
            session['message'] = result.get('message', 'Login failed')
            session['message_type'] = "error"
    except Exception as e:
        session['message'] = f"Login error: {e}"
        session['message_type'] = "error"
    
    return redirect(url_for('dashboard'))

@app.route('/logout', methods=['POST'])
def logout():
    """Logout voter"""
    session.clear()
    return jsonify({"success": True})

@app.route('/vote', methods=['POST'])
def vote():
    """Submit vote"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "Not logged in"})
    
    data = request.get_json()
    candidate = data.get('candidate')
    click_time = data.get('click_time')
    
    if not candidate or not click_time:
        return jsonify({"success": False, "message": "Missing candidate or click time"})
    
    server = get_server_connection()
    if not server:
        return jsonify({"success": False, "message": "Cannot connect to voting server"})
    
    try:
        # Get server time for timestamp
        time_response = server.GetServerTime()
        if not time_response.get('success'):
            return jsonify({"success": False, "message": "Failed to get server time"})
        
        timestamp = time_response['lamport_clock']
        
        # Submit vote
        result = server.Vote(
            session['session_id'],
            candidate,
            timestamp,
            click_time
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Vote submission error: {e}")
        return jsonify({"success": False, "message": f"Vote submission error: {e}"})

@app.route('/api/status')
def api_status():
    """API endpoint for status"""
    server = get_server_connection()
    if not server:
        return jsonify({"success": False, "message": "Cannot connect to voting server"})
    
    try:
        return jsonify(server.GetVotingStatus())
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {e}"})


def main():
    """Start the client dashboard"""
    print("Client Dashboard starting on port 5001...")
    print("Access the dashboard at: http://localhost:5001")
    print("\nDefault voters in the system:")
    print("1. Alice (ID: 1)")
    print("2. Bob (ID: 2)")
    print("3. Charlie (ID: 3)")
    print("4. Diana (ID: 4)")
    print("5. Eve (ID: 5)")
    print("6. Frank (ID: 6)")
    print("7. Grace (ID: 7)")
    print("8. Henry (ID: 8)")
    print("9. Ivy (ID: 9)")
    print("10. Jack (ID: 10)")
    
    try:
        app.run(host='localhost', port=5001, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down client dashboard...")

if __name__ == "__main__":
    main()
