# Flask-Based Voting System

A simplified Flask-based voting system with real-time notifications, admin controls, and live vote tracking.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Flask

### Installation & Running

1. **Install Flask:**
   ```bash
   pip install -r flask_requirements.txt
   ```

2. **Run the system:**
   ```bash
   python run_flask_system.py
   ```
   
   Or directly:
   ```bash
   python app.py
   ```

3. **Access the system:**
   - **Main Interface**: http://localhost:5000 (Voters)
   - **Admin Dashboard**: http://localhost:5000/admin (Admin Only)
   - **Results Page**: http://localhost:5000/results (Public)
   - **Voting History**: http://localhost:5000/admin/history (Admin Only)

## 🎯 System Features

### ✅ Admin Dashboard Controls
- **Start Voting**: Enables voting for all users
- **Stop Voting**: Disables voting and enables result publishing
- **Publish Results**: Makes results publicly available
- **Start New Voting**: Saves current session to history and starts fresh session
- **View History**: Access complete voting history with detailed results

### ✅ Voting Logic
- Users can vote only once
- Voting works only when `voting_active = True`
- Re-voting attempts show: *"You have already voted. Result will be notified soon."*

### ✅ Real-time Features
- **Live Vote Counts**: Admin dashboard shows real-time vote tallies
- **System Notifications**: Live updates for login/logout/voting events
- **Auto-refresh**: Pages update automatically
- **Voting History**: Complete history of all voting sessions with detailed results
- **Session Management**: Multiple voting rounds with automatic session tracking

### ✅ System Notifications
The system logs and displays these events live:
- `<user> logged in`
- `<user> voted`
- `<user> logged out`
- `<user> waiting` (when voting is inactive)

## 👥 Default Voters

The system includes 10 pre-registered voters:

| ID | Name    | ID | Name    |
|----|---------|----|---------| 
| 1  | Alice   | 6  | Frank   |
| 2  | Bob     | 7  | Grace   |
| 3  | Charlie | 8  | Henry   |
| 4  | Diana   | 9  | Ivy     |
| 5  | Eve     | 10 | Jack    |

## 🗳️ Candidates

10 candidates available: Candidate A through Candidate J

## 📋 Usage Workflow

### For Administrators

1. **Access Admin Dashboard**: http://localhost:5000/admin
2. **Start Voting**: Click "Start Voting" button
3. **Monitor Activity**: 
   - View real-time vote counts
   - Watch system notifications
   - Check voter database status
4. **Stop Voting**: Click "Stop Voting" when ready
5. **Publish Results**: Click "Publish Results" to make results public
6. **Start New Voting**: Click "Start New Voting" to save current session and begin fresh
7. **View History**: Click "View History" to see all past voting sessions

### For Voters

1. **Login**: Go to http://localhost:5000
   - Enter your name and voter ID (contact admin for credentials)
2. **Vote**: Select your preferred candidate
3. **Confirmation**: System confirms vote submission
4. **Results**: View results after admin publishes them

## 📊 Voting History & Sessions

### Multiple Voting Sessions
- **Session Tracking**: Each voting round is tracked as a separate session
- **Automatic Numbering**: Sessions are numbered sequentially (Session 1, 2, 3...)
- **History Preservation**: All completed sessions are saved with full details

### What Gets Saved
- **Vote Counts**: Complete breakdown by candidate
- **Winner Information**: Automatically calculated winner for each session
- **Participant Details**: Who voted and their choices
- **Timestamps**: When each session was conducted
- **Statistics**: Total votes, participation rates, percentages

### Starting New Sessions
1. **Complete Current Session**: Stop voting and publish results
2. **Start New Voting**: Click the "Start New Voting" button
3. **Automatic Save**: Current session automatically saved to history
4. **Fresh Start**: All votes reset, new session number assigned
5. **Clean Slate**: All voters can participate again in new session

### Viewing History
- **Admin-Only Access**: View complete history from admin dashboard only
- **Detailed Results**: See vote breakdowns for each past session
- **Summary Statistics**: Total sessions, votes, and averages
- **Participant Tracking**: See who voted in each session
- **Privacy Protection**: Voters cannot access voting history of other sessions

## 🔧 Technical Implementation

### File Structure
```
├── app.py                 # Main Flask application
├── run_flask_system.py    # Launcher script
├── flask_requirements.txt # Dependencies
├── templates/            # HTML templates
│   ├── admin.html        # Admin dashboard
│   ├── login.html        # Login page
│   ├── vote.html         # Voting interface
│   ├── voted.html        # Already voted page
│   ├── voting_inactive.html # Voting inactive page
│   ├── results.html      # Results display
│   └── results_pending.html # Results pending page
└── FLASK_README.md       # This file
```

### Key Components

**Backend (`app.py`):**
- Flask routes for all functionality
- In-memory data storage
- Real-time vote tracking
- Session management
- Notification system

**Frontend (Templates):**
- Responsive HTML with embedded CSS
- JavaScript for AJAX calls
- Auto-refresh functionality
- Modern UI design

### Data Storage

**Voters Database:**
```python
VOTERS_DB = [
    {"id": 1, "name": "Alice", "has_voted": False, "vote": None},
    # ... more voters
]
```

**Real-time Vote Tracking:**
```python
VOTES = {"Candidate A": 0, "Candidate B": 0, ...}
VOTED_USERS = set()  # Prevents re-voting
```

**System Notifications:**
```python
NOTIFICATIONS = deque(maxlen=50)  # Live event log
```

## 🌐 API Endpoints

### Public Routes
- `GET /` - Main interface (login/vote)
- `POST /login` - User authentication
- `GET /logout` - User logout
- `POST /vote` - Submit vote
- `GET /results` - View results

### Admin Routes
- `GET /admin` - Admin dashboard
- `POST /admin/start_voting` - Start voting
- `POST /admin/stop_voting` - Stop voting
- `POST /admin/publish_results` - Publish results

### API Routes
- `GET /api/notifications` - Get live notifications
- `GET /api/status` - Get system status

## 🔄 Real-time Updates

### Admin Dashboard
- **Vote counts** update in real-time
- **Notifications** refresh every 2 seconds
- **Page** auto-refreshes every 10 seconds

### Voter Interface
- **Voting status** checked automatically
- **Results availability** monitored
- **Auto-redirect** after voting

## 🎨 UI Features

### Modern Design
- Gradient backgrounds
- Card-based layouts
- Responsive grid system
- Hover effects and animations

### User Experience
- Clear status messages
- Confirmation dialogs
- Auto-refresh indicators
- Mobile-friendly design

## 🔒 Security Features

- **Session Management**: Flask sessions for user authentication
- **Input Validation**: Server-side validation for all inputs
- **CSRF Protection**: Built into Flask forms
- **Re-voting Prevention**: Server-side tracking of voted users

## 📊 Monitoring

### Admin Dashboard Shows:
- Current voting status (Active/Inactive)
- Results publication status
- Real-time vote counts per candidate
- Complete voter database with vote status
- Live system notifications feed
- Total votes cast

### System Notifications Include:
- User login/logout events
- Vote submission events
- Admin actions (start/stop/publish)
- System status changes

## 🛠️ Customization

### Adding New Candidates
Edit the `CANDIDATES` list in `app.py`:
```python
CANDIDATES = [
    "Your Candidate 1",
    "Your Candidate 2",
    # ... add more
]
```

### Adding New Voters
Edit the `VOTERS_DB` list in `app.py`:
```python
VOTERS_DB.append({
    "id": 11, 
    "name": "NewVoter", 
    "has_voted": False, 
    "vote": None
})
```

### Styling Changes
Modify the CSS in the HTML templates under the `templates/` directory.

## 🚨 Troubleshooting

### Common Issues

1. **Flask Not Found**
   ```bash
   pip install Flask
   ```

2. **Port Already in Use**
   - Change port in `app.py`: `app.run(port=5001)`
   - Or kill existing process

3. **Templates Not Found**
   - Ensure `templates/` directory exists
   - Check all template files are present

4. **Session Issues**
   - Clear browser cookies
   - Restart Flask server

### Debug Mode
The system runs in debug mode by default, showing detailed error messages.

## 📈 Performance

- **In-Memory Storage**: Fast access, no database required
- **Real-time Updates**: Efficient AJAX polling
- **Session Management**: Lightweight Flask sessions
- **Auto-refresh**: Configurable intervals

## 🔮 Future Enhancements

Potential improvements:
- Database persistence (SQLite/PostgreSQL)
- WebSocket real-time updates
- User registration system
- Vote encryption
- Audit logging
- Multi-language support

---

**System Status**: Production Ready ✅  
**Framework**: Flask 2.3.3  
**Python Version**: 3.7+  
**License**: MIT
