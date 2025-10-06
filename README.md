# Distributed Voting System

A comprehensive distributed voting system implemented in Python using XML-RPC for communication, Flask for web dashboards, and featuring replication, mutual exclusion, and load balancing.

## 🏗️ System Architecture

### Components

1. **Voting Server** (`server.py`) - Primary server handling vote processing
2. **Replica Servers** (`replica.py`) - Synchronous replication for fault tolerance  
3. **Tally Server** (`tally_server.py`) - Vote counting and result publishing
4. **Client Dashboard** (`client.py`) - Web interface for voters
5. **Admin Dashboard** (`admin_dashboard.py`) - Administrative control panel

### Key Features

- **RPC Communication**: XML-RPC for inter-component communication
- **Mutual Exclusion**: Lamport timestamps with conflict resolution
- **Replication**: 3-server setup with majority consensus (2/3)
- **Load Balancing**: Queue-based processing with configurable concurrency
- **Time Synchronization**: Berkeley algorithm implementation
- **Real-time Notifications**: Live updates for voting activity
- **Web Dashboards**: Modern responsive interfaces

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Flask (automatically installed)

### Installation

1. **Clone or download all system files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the System

#### Option 1: Automated Startup (Recommended)
```bash
python start_system.py
```

This will start all components automatically with proper delays.

#### Option 2: Manual Startup

Start each component in separate terminals:

```bash
# Terminal 1: Main Server
python server.py

# Terminal 2: Replica 1  
python replica.py 8001

# Terminal 3: Replica 2
python replica.py 8002

# Terminal 4: Tally Server
python tally_server.py

# Terminal 5: Client Dashboard
python client.py

# Terminal 6: Admin Dashboard
python admin_dashboard.py
```

## 🌐 Access Points

Once running, access these web interfaces:

- **Client Dashboard**: http://localhost:5001 (Voters)
- **Admin Dashboard**: http://localhost:5002 (Administrators)  
- **Tally Dashboard**: http://localhost:5003 (Results)

## 👥 Default Voters

The system comes with 10 pre-registered voters:

| ID | Name    | ID | Name    |
|----|---------|----|---------| 
| 1  | Alice   | 6  | Frank   |
| 2  | Bob     | 7  | Grace   |
| 3  | Charlie | 8  | Henry   |
| 4  | Diana   | 9  | Ivy     |
| 5  | Eve     | 10 | Jack    |

## 🗳️ Usage Workflow

### For Administrators

1. **Access Admin Dashboard** at http://localhost:5002
2. **Set Voting Deadline**: Choose date/time or minutes from now
3. **Start Voting**: Click "Start Voting" button
4. **Monitor Progress**: View live voter database and notifications
5. **Stop Voting**: Click "Stop Voting" when ready
6. **Publish Results**: Send votes to tally server and announce winner

### For Voters

1. **Access Client Dashboard** at http://localhost:5001
2. **Login**: Use your name and ID from the default voters list
3. **Vote**: Select your preferred candidate from the 10 options
4. **View Results**: See results after admin publishes them

### For Monitoring

1. **Tally Dashboard** at http://localhost:5003 shows:
   - Live vote counting
   - Results when published
   - Winner announcement

## 🔧 System Features

### RPC Endpoints

**Voting Server (Port 8000):**
- `Register(name)` - Add new voter
- `Login(name, id)` - Authenticate voter
- `GetOptions()` - Get candidate list
- `Vote(session_id, candidate, timestamp, click_time)` - Submit vote
- `GetServerTime()` - Time synchronization
- `StreamNotifications()` - Get activity logs
- `SetTimer(end_time)` - Set voting deadline (Admin)
- `StartVote()` - Start voting (Admin)
- `StopVote()` - Stop voting (Admin)
- `PublishResults()` - Publish to tally server (Admin)

**Replica Servers (Ports 8001, 8002):**
- `ReplicateUpdate(operation, data)` - Receive replication updates
- `GetReplicaStatus()` - Health and status info
- `HealthCheck()` - Availability check

**Tally Server (Port 8003):**
- `SubmitVotes(votes)` - Receive votes from main server
- `GetResults()` - Get voting results
- `PublishResults()` - Make results public

### Concurrency & Mutual Exclusion

- **Lamport Timestamps**: Each operation gets a logical timestamp
- **Conflict Resolution**: Lower timestamp wins; ties broken by voter ID
- **Load Balancing**: Max 5 concurrent votes, others queued
- **Deadlock Prevention**: Timeout mechanisms and priority ordering

### Replication Strategy

- **Synchronous Replication**: Updates sent to all replicas
- **Majority Consensus**: Requires 2/3 replicas to acknowledge
- **Automatic Rollback**: Failed replications are undone
- **Health Monitoring**: Replica status tracked in admin dashboard

### Time Synchronization

- **Server Time Authority**: All operations use server timestamps
- **Deadline Enforcement**: Based on click time, not processing time
- **Berkeley Algorithm**: Periodic time sync broadcasts

## 🛠️ Configuration

### Server Settings (in `server.py`)

```python
# Concurrency limits
self.max_concurrent_votes = 5

# Replica ports  
self.replica_ports = [8001, 8002]

# Time sync interval
time.sleep(5)  # 5-second broadcasts
```

### Port Configuration

| Component | Port | Purpose |
|-----------|------|---------|
| Main Server | 8000 | RPC endpoint |
| Replica 1 | 8001 | RPC endpoint |
| Replica 2 | 8002 | RPC endpoint |
| Tally Server | 8003 | RPC endpoint |
| Client Dashboard | 5001 | Web interface |
| Admin Dashboard | 5002 | Web interface |
| Tally Dashboard | 5003 | Web interface |

## 🔍 Monitoring & Debugging

### Log Files

Each component outputs logs to console showing:
- RPC calls and responses
- Replication status
- Vote processing
- Error conditions

### Admin Dashboard Features

- **Live Database View**: See all voters and their status
- **Replication Status**: Health of all replica servers
- **System Notifications**: Real-time activity feed
- **Vote Queue Status**: Current processing load

### Health Checks

- Replica servers provide health endpoints
- Admin dashboard shows replica connectivity
- Automatic failover handling (graceful degradation)

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Check if components are already running
   - Kill existing processes: `pkill -f "python server.py"`

2. **Connection Refused**
   - Ensure all components started successfully
   - Check firewall settings
   - Verify port availability

3. **Replication Failures**
   - Check replica server logs
   - Restart failed replicas
   - System continues with reduced redundancy

4. **Vote Processing Delays**
   - Normal for high load (queue system working)
   - Check admin dashboard for queue status
   - Increase `max_concurrent_votes` if needed

### Performance Tuning

- **Concurrent Votes**: Adjust `max_concurrent_votes` in server.py
- **Queue Size**: Monitor via admin dashboard
- **Time Sync Frequency**: Modify sleep interval in `_broadcast_time_sync`
- **Notification Buffer**: Adjust `maxlen` in notifications deque

## 📊 System Specifications

- **Scalability**: Supports hundreds of concurrent voters
- **Fault Tolerance**: Continues operation with 1 replica failure
- **Consistency**: Strong consistency through majority consensus
- **Availability**: High availability with graceful degradation
- **Performance**: Queue-based load balancing prevents overload

## 🔒 Security Considerations

- **Session Management**: Unique session IDs for authenticated users
- **Vote Integrity**: Lamport timestamps prevent replay attacks
- **Access Control**: Admin functions separated from voter interface
- **Data Validation**: Input sanitization and type checking

## 📝 Development Notes

- Built with Python standard library + Flask
- Modular design for easy extension
- Comprehensive error handling
- Responsive web interfaces
- Real-time updates via auto-refresh

## 🤝 Contributing

To extend the system:

1. **Add New RPC Methods**: Extend server classes
2. **Enhance UI**: Modify HTML templates in dashboard files
3. **Improve Algorithms**: Update mutual exclusion or replication logic
4. **Add Features**: Implement additional voting mechanisms

---

**System Status**: Production Ready ✅  
**Last Updated**: October 2024  
**Python Version**: 3.7+  
**License**: MIT
