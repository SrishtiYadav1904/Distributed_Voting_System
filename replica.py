#!/usr/bin/env python3
"""
Distributed Voting System - Replica Server
Maintains synchronized copy of the main server's data
"""

import threading
import time
import sys
from xmlrpc.server import SimpleXMLRPCServer
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReplicaServer:
    def __init__(self, port):
        self.port = port
        
        # Replica of voter database
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
        
        # Replica state
        self.voting_active = False
        self.voting_deadline = None
        self.results_published = False
        
        # Thread safety
        self.db_lock = threading.Lock()
        
        logger.info(f"Replica server initialized on port {port}")
    
    def ReplicateUpdate(self, operation, data):
        """Handle replication updates from primary server"""
        try:
            with self.db_lock:
                if operation == "vote":
                    # Update voter's vote status
                    voter_id = data["voter_id"]
                    candidate = data["candidate"]
                    
                    for voter in self.voters_db:
                        if voter["id"] == voter_id:
                            voter["has_voted"] = True
                            voter["vote"] = candidate
                            logger.info(f"Replicated vote: Voter {voter_id} voted for {candidate}")
                            break
                
                elif operation == "register":
                    # Add new voter
                    new_voter = data.copy()
                    
                    # Check if voter already exists
                    exists = False
                    for voter in self.voters_db:
                        if voter["id"] == new_voter["id"]:
                            exists = True
                            break
                    
                    if not exists:
                        self.voters_db.append(new_voter)
                        logger.info(f"Replicated registration: {new_voter['name']} (ID: {new_voter['id']})")
                
                elif operation == "set_timer":
                    # Update voting deadline
                    self.voting_deadline = data["end_time"]
                    logger.info(f"Replicated timer setting: {datetime.fromtimestamp(data['end_time'])}")
                
                elif operation == "start_vote":
                    # Start voting
                    self.voting_active = True
                    self.results_published = False
                    logger.info("Replicated voting start")
                
                elif operation == "stop_vote":
                    # Stop voting
                    self.voting_active = False
                    logger.info("Replicated voting stop")
                
                elif operation == "publish_results":
                    # Mark results as published
                    self.results_published = True
                    logger.info("Replicated results publication")
                
                else:
                    logger.warning(f"Unknown replication operation: {operation}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing replication update: {e}")
            return False
    
    def GetVoterDatabase(self):
        """Get current voter database (for debugging/monitoring)"""
        with self.db_lock:
            return {"success": True, "voters": self.voters_db.copy()}
    
    def GetReplicaStatus(self):
        """Get replica status"""
        return {
            "success": True,
            "port": self.port,
            "voting_active": self.voting_active,
            "deadline": self.voting_deadline,
            "results_published": self.results_published,
            "voter_count": len(self.voters_db)
        }
    
    def HealthCheck(self):
        """Health check endpoint"""
        return {"success": True, "status": "healthy", "port": self.port}

def main():
    """Start the replica server"""
    if len(sys.argv) != 2:
        print("Usage: python replica.py <port>")
        print("Example: python replica.py 8001")
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Error: Port must be a number")
        sys.exit(1)
    
    replica = ReplicaServer(port)
    
    # Create XML-RPC server
    rpc_server = SimpleXMLRPCServer(("localhost", port), allow_none=True)
    rpc_server.register_instance(replica)
    
    print(f"Replica Server starting on port {port}...")
    print("Available RPC methods:")
    print("- ReplicateUpdate(operation, data)")
    print("- GetVoterDatabase()")
    print("- GetReplicaStatus()")
    print("- HealthCheck()")
    
    try:
        rpc_server.serve_forever()
    except KeyboardInterrupt:
        print(f"\nShutting down replica server on port {port}...")
        rpc_server.shutdown()

if __name__ == "__main__":
    main()
