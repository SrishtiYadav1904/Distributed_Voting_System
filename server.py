#!/usr/bin/env python3
"""
Distributed Voting System - Main Server
Implements RPC endpoints, mutual exclusion, replication, and load balancing
"""

import threading
import time
import json
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from collections import deque
import heapq
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VotingServer:
    def __init__(self, port=8000, replica_ports=[8001, 8002]):
        self.port = port
        self.replica_ports = replica_ports
        self.replicas = []
        
        # Lamport clock for mutual exclusion
        self.lamport_clock = 0
        self.clock_lock = threading.Lock()
        
        # Voter database - static in-memory array
        self.voters_db = [
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
        
        # Candidates list
        self.candidates = [
            "Candidate A", "Candidate B", "Candidate C", "Candidate D", "Candidate E",
            "Candidate F", "Candidate G", "Candidate H", "Candidate I", "Candidate J"
        ]
        
        # Voting state
        self.voting_active = False
        self.voting_deadline = None
        self.results_published = False
        
        # Concurrency control
        self.max_concurrent_votes = 5
        self.active_votes = 0
        # Use a priority queue (heap) for votes to enforce ordering by (timestamp, voter_id)
        # Each heap entry: (timestamp, voter_id, counter, vote_request)
        self.vote_queue = []
        self.vote_queue_lock = threading.Lock()
        self.vote_counter = 0  # tie-breaker for heap entries
        self.vote_lock = threading.Lock()
        # Track voter ids currently being processed to prevent concurrent votes by same voter
        self.in_progress_votes = set()
        self.in_progress_lock = threading.Lock()
        
        # Session management
        self.active_sessions = {}
        self.session_lock = threading.Lock()
        
        # Notifications and logs
        self.notifications = deque(maxlen=100)
        self.notification_subscribers = []
        self.notification_lock = threading.Lock()
        
        # Database lock for thread safety
        self.db_lock = threading.Lock()
        
        # Start background threads
        self.start_background_threads()
        
    def start_background_threads(self):
        """Start background threads for queue processing and time sync"""
        # Vote queue processor
        queue_thread = threading.Thread(target=self._process_vote_queue, daemon=True)
        queue_thread.start()
        
        # Time sync broadcaster
        sync_thread = threading.Thread(target=self._broadcast_time_sync, daemon=True)
        sync_thread.start()
        
    def _increment_lamport_clock(self):
        """Increment Lamport clock"""
        with self.clock_lock:
            self.lamport_clock += 1
            return self.lamport_clock
    
    def _update_lamport_clock(self, received_clock):
        """Update Lamport clock based on received timestamp"""
        with self.clock_lock:
            self.lamport_clock = max(self.lamport_clock, received_clock) + 1
            return self.lamport_clock
    
    def _add_notification(self, message):
        """Add notification to the log"""
        timestamp = datetime.now().isoformat()
        notification = {"timestamp": timestamp, "message": message}
        
        with self.notification_lock:
            self.notifications.append(notification)
            logger.info(f"Notification: {message}")
    
    def _replicate_to_replicas(self, operation, data):
        """Replicate operation to replica servers"""
        successful_replicas = 0
        
        for replica_port in self.replica_ports:
            try:
                replica = ServerProxy(f"http://localhost:{replica_port}")
                result = replica.ReplicateUpdate(operation, data)
                if result:
                    successful_replicas += 1
            except Exception as e:
                logger.error(f"Failed to replicate to replica on port {replica_port}: {e}")
        
        # Require majority (2 out of 3 including primary)
        return successful_replicas >= 1  # Need at least 1 replica + primary = majority
    
    def _process_vote_queue(self):
        """Background thread to process queued votes (priority-based).

        Votes are ordered by (timestamp, voter_id) so earlier clicks or lower-id voters get priority.
        If a voter's vote is already being processed, their queued vote is requeued.
        """
        while True:
            try:
                if self.active_votes < self.max_concurrent_votes:
                    # Pop highest-priority vote
                    with self.vote_queue_lock:
                        if not self.vote_queue:
                            time.sleep(0.1)
                            continue
                        _, _, _, vote_request = heapq.heappop(self.vote_queue)

                    session_id = vote_request[0]

                    # Lookup voter id from session
                    with self.session_lock:
                        voter_info = self.active_sessions.get(session_id)

                    if not voter_info:
                        # Invalid session; skip
                        self._add_notification(f"Dropped queued vote for invalid session {session_id}")
                        continue

                    voter_id = voter_info.get("id")

                    # If voter already being processed, requeue and wait
                    with self.in_progress_lock:
                        if voter_id in self.in_progress_votes:
                            # requeue
                            with self.vote_queue_lock:
                                heapq.heappush(self.vote_queue, (vote_request[2], voter_id, self.vote_counter, vote_request))
                                self.vote_counter += 1
                            time.sleep(0.05)
                            continue
                        else:
                            # mark as in-progress
                            self.in_progress_votes.add(voter_id)

                    # Process the vote in a separate thread
                    vote_thread = threading.Thread(
                        target=self._process_single_vote,
                        args=(vote_request,),
                        daemon=True
                    )
                    vote_thread.start()
                else:
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in vote queue processing: {e}")
    
    def _process_single_vote(self, vote_request):
        """Process a single vote request"""
        session_id, candidate, timestamp, click_time = vote_request
        # Attempt to determine voter id from session
        with self.session_lock:
            voter_info = self.active_sessions.get(session_id)

        voter_id = None
        if voter_info:
            voter_id = voter_info.get("id")

        # Mark active vote and increment counters
        with self.vote_lock:
            self.active_votes += 1

        # Ensure this voter is marked in-progress (should have been marked by queue processor)
        marked_in_progress = False
        if voter_id is not None:
            with self.in_progress_lock:
                if voter_id not in self.in_progress_votes:
                    self.in_progress_votes.add(voter_id)
                    marked_in_progress = True
        
        try:
            # Validate session
            if not voter_info:
                return {"success": False, "message": "Invalid session"}
            
            # Check if voting is active and within deadline
            if not self.voting_active:
                return {"success": False, "message": "Voting is not active"}
            
            if self.voting_deadline and click_time > self.voting_deadline:
                return {"success": False, "message": "Vote submitted after deadline"}
            
            # Update Lamport clock
            self._update_lamport_clock(timestamp)
            
            # Find voter in database
            with self.db_lock:
                voter = None
                for v in self.voters_db:
                    if v["id"] == voter_info["id"] and v["name"] == voter_info["name"]:
                        voter = v
                        break
                
                if not voter:
                    return {"success": False, "message": "Voter not found"}
                
                if voter["has_voted"]:
                    return {"success": False, "message": "Already voted"}
                
                # Record the vote
                voter["has_voted"] = True
                voter["vote"] = candidate
                
                # Replicate to replicas
                replication_data = {
                    "voter_id": voter["id"],
                    "candidate": candidate,
                    "timestamp": timestamp
                }
                
                if self._replicate_to_replicas("vote", replication_data):
                    self._add_notification(f"{voter['name']} voted for {candidate}")
                    return {"success": True, "message": "Vote recorded successfully"}
                else:
                    # Rollback if replication failed
                    voter["has_voted"] = False
                    voter["vote"] = None
                    return {"success": False, "message": "Replication failed"}
        
        finally:
            # Decrement active_votes and clear in-progress marker for this voter
            with self.vote_lock:
                self.active_votes -= 1

            if voter_id is not None:
                with self.in_progress_lock:
                    if voter_id in self.in_progress_votes:
                        # Only remove if we added it here or it's still present
                        try:
                            self.in_progress_votes.remove(voter_id)
                        except KeyError:
                            pass
    
    def _broadcast_time_sync(self):
        """Broadcast time synchronization to clients"""
        while True:
            try:
                time.sleep(5)  # Broadcast every 5 seconds
                current_time = time.time()
                # In a real implementation, this would broadcast to subscribed clients
                logger.debug(f"Broadcasting time sync: {current_time}")
            except Exception as e:
                logger.error(f"Error in time sync broadcast: {e}")
    
    # RPC Methods
    def Register(self, name):
        """Register a new voter"""
        self._increment_lamport_clock()
        
        with self.db_lock:
            # Check if voter already exists
            for voter in self.voters_db:
                if voter["name"] == name:
                    return {"success": True, "id": voter["id"], "message": "Voter already registered"}
            
            # Add new voter
            new_id = len(self.voters_db) + 1
            new_voter = {"id": new_id, "name": name, "has_voted": False, "vote": None}
            self.voters_db.append(new_voter)
            
            # Replicate to replicas
            if self._replicate_to_replicas("register", new_voter):
                self._add_notification(f"New voter registered: {name} (ID: {new_id})")
                return {"success": True, "id": new_id, "message": "Registration successful"}
            else:
                # Rollback
                self.voters_db.pop()
                return {"success": False, "message": "Registration failed due to replication error"}
    
    def Login(self, name, voter_id):
        """Login voter and create session"""
        self._increment_lamport_clock()
        
        with self.db_lock:
            # Verify credentials
            voter = None
            for v in self.voters_db:
                if v["id"] == voter_id and v["name"] == name:
                    voter = v
                    break
            
            if not voter:
                return {"success": False, "message": "Invalid credentials"}
            
            # Create session
            session_id = f"session_{voter_id}_{int(time.time())}"
            
            with self.session_lock:
                self.active_sessions[session_id] = {
                    "id": voter_id,
                    "name": name,
                    "login_time": time.time()
                }
            
            self._add_notification(f"{name} logged in")
            return {
                "success": True,
                "session_id": session_id,
                "has_voted": voter["has_voted"],
                "message": "Login successful"
            }
    
    def GetOptions(self):
        """Get list of candidates"""
        return {"success": True, "candidates": self.candidates}
    
    def Vote(self, session_id, candidate, timestamp, click_time):
        """Submit a vote (queued processing)"""
        self._increment_lamport_clock()
        
        # Validate candidate
        if candidate not in self.candidates:
            return {"success": False, "message": "Invalid candidate"}
        # Prepare vote request
        vote_request = (session_id, candidate, timestamp, click_time)

        # Resolve voter id for priority ordering
        with self.session_lock:
            voter_info = self.active_sessions.get(session_id)

        if not voter_info:
            return {"success": False, "message": "Invalid session"}

        voter_id = voter_info.get("id")

        # Push into priority heap
        with self.vote_queue_lock:
            heapq.heappush(self.vote_queue, (timestamp, voter_id, self.vote_counter, vote_request))
            self.vote_counter += 1
            queue_size = len(self.vote_queue)

        self._add_notification(f"Vote request queued (queue size: {queue_size})")

        return {"success": True, "message": "Vote queued for processing", "queued": True}
    
    def GetServerTime(self):
        """Get current server time"""
        return {"success": True, "server_time": time.time(), "lamport_clock": self.lamport_clock}
    
    def StreamNotifications(self):
        """Get recent notifications"""
        with self.notification_lock:
            return {"success": True, "notifications": list(self.notifications)}
    
    def GetVoterDatabase(self):
        """Get current voter database (admin function)"""
        with self.db_lock:
            return {"success": True, "voters": self.voters_db.copy()}
    
    def SetTimer(self, end_time):
        """Set voting deadline (admin function)"""
        self.voting_deadline = end_time
        self._add_notification(f"Voting deadline set to {datetime.fromtimestamp(end_time)}")
        
        # Replicate to replicas
        self._replicate_to_replicas("set_timer", {"end_time": end_time})
        return {"success": True, "message": "Timer set successfully"}
    
    def StartVote(self):
        """Start voting (admin function)"""
        self.voting_active = True
        self.results_published = False
        self._add_notification("Voting started")
        
        # Replicate to replicas
        self._replicate_to_replicas("start_vote", {})
        return {"success": True, "message": "Voting started"}
    
    def StopVote(self):
        """Stop voting (admin function)"""
        self.voting_active = False
        self._add_notification("Voting stopped")
        
        # Replicate to replicas
        self._replicate_to_replicas("stop_vote", {})
        return {"success": True, "message": "Voting stopped"}
    
    def PublishResults(self):
        """Publish results to tally server (admin function)"""
        if self.voting_active:
            return {"success": False, "message": "Cannot publish results while voting is active"}
        
        # Collect votes
        votes = []
        with self.db_lock:
            for voter in self.voters_db:
                if voter["has_voted"] and voter["vote"]:
                    votes.append(voter["vote"])
        


def main():
    """Start the voting server"""
    server = VotingServer()
    
    # Create XML-RPC server
    rpc_server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    rpc_server.register_instance(server)
    
    print("Voting Server starting on port 8000...")
    print("Available RPC methods:")
    print("- Register(name)")
    print("- Login(name, id)")
    print("- GetOptions()")
    print("- Vote(session_id, candidate, timestamp, click_time)")
    print("- GetServerTime()")
    print("- StreamNotifications()")
    print("- GetVoterDatabase()")
    print("- SetTimer(end_time)")
    print("- StartVote()")
    print("- StopVote()")
    print("- PublishResults()")
    print("- GetVotingStatus()")
    
    try:
        rpc_server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        rpc_server.shutdown()

if __name__ == "__main__":
    main()
