#!/usr/bin/env python3
"""
Demo script to showcase the new voting history features
This script simulates multiple voting sessions to demonstrate the history functionality
"""

import time
import requests
import json

def demo_voting_sessions():
    """Demonstrate multiple voting sessions with history"""
    
    print("🎬 Voting History Demo")
    print("=" * 50)
    print("This demo will simulate multiple voting sessions to show the history feature.")
    print("Make sure the Flask app is running on http://localhost:5000")
    print()
    
    base_url = "http://localhost:5000"
    
    # Check if server is running
    try:
        response = requests.get(base_url)
        if response.status_code != 200:
            print("❌ Flask server not responding. Please start the app first.")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Please start the app first:")
        print("   python app.py")
        return
    
    print("✅ Flask server is running")
    print()
    
    # Demo scenarios
    scenarios = [
        {
            "name": "Session 1: Close Election",
            "votes": [
                ("Alice", 1, "Candidate A"),
                ("Bob", 2, "Candidate B"),
                ("Charlie", 3, "Candidate A"),
                ("Diana", 4, "Candidate C"),
                ("Eve", 5, "Candidate A")
            ]
        },
        {
            "name": "Session 2: Landslide Victory", 
            "votes": [
                ("Alice", 1, "Candidate B"),
                ("Bob", 2, "Candidate B"),
                ("Charlie", 3, "Candidate B"),
                ("Diana", 4, "Candidate B"),
                ("Eve", 5, "Candidate A"),
                ("Frank", 6, "Candidate B")
            ]
        },
        {
            "name": "Session 3: Three-Way Race",
            "votes": [
                ("Alice", 1, "Candidate A"),
                ("Bob", 2, "Candidate B"),
                ("Charlie", 3, "Candidate C"),
                ("Diana", 4, "Candidate A"),
                ("Eve", 5, "Candidate B"),
                ("Frank", 6, "Candidate C"),
                ("Grace", 7, "Candidate A")
            ]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"🗳️ Running {scenario['name']}...")
        
        # Start voting
        print("   Starting voting...")
        response = requests.post(f"{base_url}/admin/start_voting")
        if response.status_code == 200:
            print("   ✅ Voting started")
        else:
            print("   ❌ Failed to start voting")
            continue
        
        # Simulate votes
        print(f"   Casting {len(scenario['votes'])} votes...")
        for name, voter_id, candidate in scenario['votes']:
            # Login
            login_data = {"name": name, "voter_id": voter_id}
            session = requests.Session()
            login_response = session.post(f"{base_url}/login", data=login_data)
            
            if login_response.status_code == 200:
                # Vote
                vote_data = {"candidate": candidate}
                vote_response = session.post(f"{base_url}/vote", json=vote_data)
                if vote_response.status_code == 200:
                    result = vote_response.json()
                    if result.get("success"):
                        print(f"     ✅ {name} voted for {candidate}")
                    else:
                        print(f"     ⚠️ {name}: {result.get('message', 'Vote failed')}")
                else:
                    print(f"     ❌ {name}: Vote request failed")
            else:
                print(f"     ❌ {name}: Login failed")
            
            time.sleep(0.5)  # Small delay between votes
        
        # Stop voting
        print("   Stopping voting...")
        response = requests.post(f"{base_url}/admin/stop_voting")
        if response.status_code == 200:
            print("   ✅ Voting stopped")
        
        # Publish results
        print("   Publishing results...")
        response = requests.post(f"{base_url}/admin/publish_results")
        if response.status_code == 200:
            print("   ✅ Results published")
        
        # Start new voting (except for last session)
        if i < len(scenarios):
            print("   Starting new voting session...")
            response = requests.post(f"{base_url}/admin/start_new_voting")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result.get('message', 'New session started')}")
            else:
                print("   ❌ Failed to start new session")
        
        print(f"   ✅ {scenario['name']} completed!")
        print()
        time.sleep(1)
    
    print("🎉 Demo completed!")
    print()
    print("Now you can:")
    print(f"📊 View Admin Dashboard: {base_url}/admin")
    print(f"📋 View Voting History: {base_url}/admin/history")
    print(f"📈 View Current Results: {base_url}/results")
    print()
    print("The history should now show 3 completed voting sessions with different results!")

if __name__ == "__main__":
    demo_voting_sessions()
