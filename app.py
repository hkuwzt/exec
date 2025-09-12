from flask import Flask, render_template, request, jsonify, g
import pandas as pd
import json
from datetime import datetime, timedelta
from dateutil import parser
import os
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)

class RequestLog(db.Model):
    __tablename__ = "request_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    method = db.Column(db.String(10))
    path = db.Column(db.String(255))
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)
    remote_addr = db.Column(db.String(45))
    user_agent = db.Column(db.Text)

class UserActivity(db.Model):
    __tablename__ = "user_activity"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    activity_type = db.Column(db.String(50))  # 'site_visit', 'calendar_export', 'course_selection', etc.
    details = db.Column(db.Text)  # JSON string with additional details
    remote_addr = db.Column(db.String(45))
    user_agent = db.Column(db.Text)

# Custom statistics middleware
@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    try:
        response_time = (time.time() - g.start_time) * 1000  # Convert to milliseconds
        
        # Log the request
        log_entry = RequestLog(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            response_time=response_time,
            remote_addr=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        # Don't let logging errors crash the app
        print(f"Logging error: {e}")
        db.session.rollback()
    
    return response

def log_user_activity(activity_type, details=None):
    """Helper function to log user activities"""
    try:
        activity = UserActivity(
            activity_type=activity_type,
            details=json.dumps(details) if details else None,
            remote_addr=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        print(f"Activity logging error: {e}")
        db.session.rollback()

# Create tables within application context
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

class CourseScheduler:
    def __init__(self, courses_info='courses_info.csv', course_sessions='course_sessions.csv'):
        self.courses_info_file = courses_info
        self.course_sessions_file = course_sessions
        self.courses_info_df = self.load_courses_info()
        self.course_sessions_df = self.load_course_sessions()
    
    def load_courses_info(self):
        """Load basic course information from CSV file"""
        try:
            if not os.path.exists(self.courses_info_file):
                print(f"Warning: {self.courses_info_file} not found, creating empty DataFrame")
                return pd.DataFrame(columns=['course_id', 'course_name', 'instructor', 'location', 'program'])
            return pd.read_csv(self.courses_info_file)
        except Exception as e:
            print(f"Error loading course info: {e}")
            return pd.DataFrame(columns=['course_id', 'course_name', 'instructor', 'location', 'program'])
    
    def load_course_sessions(self):
        """Load course sessions from CSV file"""
        try:
            if not os.path.exists(self.course_sessions_file):
                print(f"Warning: {self.course_sessions_file} not found, creating empty DataFrame")
                return pd.DataFrame(columns=['course_id', 'date', 'start_time', 'end_time'])
            df = pd.read_csv(self.course_sessions_file)
            df['start_datetime'] = pd.to_datetime(df['date'] + ' ' + df['start_time'])
            df['end_datetime'] = pd.to_datetime(df['date'] + ' ' + df['end_time'])
            return df
        except Exception as e:
            print(f"Error loading course sessions: {e}")
            return pd.DataFrame(columns=['course_id', 'date', 'start_time', 'end_time', 'start_datetime', 'end_datetime'])
    
    def get_all_courses(self):
        """Return all courses as a list of dictionaries with first session info"""
        courses = self.courses_info_df.to_dict('records')
        
        # Add first session information to each course for sorting
        for course in courses:
            first_session = self.get_first_session(course['course_id'])
            course['first_session_date'] = first_session['date'] if first_session else '9999-12-31'
            course['first_session_time'] = first_session['start_time'] if first_session else '23:59'
            course['first_session_datetime'] = first_session['datetime'] if first_session else None
        
        # Sort courses by first session datetime
        courses.sort(key=lambda x: x['first_session_datetime'] if x['first_session_datetime'] else datetime.max)
        
        return courses
    
    def get_first_session(self, course_id):
        """Get the first session for a given course"""
        course_sessions = self.course_sessions_df[self.course_sessions_df['course_id'] == course_id]
        if course_sessions.empty:
            return None
        
        # Sort by date and time to get the earliest session
        first_session = course_sessions.loc[course_sessions['start_datetime'].idxmin()]
        return {
            'date': first_session['date'],
            'start_time': first_session['start_time'],
            'datetime': first_session['start_datetime']
        }
    
    def get_courses_by_program(self, program):
        """Filter courses by program and sort by first session"""
        if program == 'All':
            return self.get_all_courses()
        
        # Get all courses first (which includes sorting)
        all_courses = self.get_all_courses()
        
        # Filter by program while maintaining the sort order
        filtered_courses = [course for course in all_courses if course['program'] == program]
        
        return filtered_courses
    
    def get_programs(self):
        """Get all unique programs"""
        try:
            if self.courses_info_df.empty:
                return ['Core Courses', 'Elective Courses', 'Other Events']  # Default programs
            return sorted(self.courses_info_df['program'].unique().tolist())
        except Exception as e:
            print(f"Error getting programs: {e}")
            return ['Core Courses', 'Elective Courses', 'Other Events']
    
    def find_overlapping_courses(self, selected_courses):
        """Find courses that have time conflicts"""
        overlaps = []
        
        for i, course1 in enumerate(selected_courses):
            sessions1 = self.course_sessions_df[self.course_sessions_df['course_id'] == course1['course_id']]
            for j, course2 in enumerate(selected_courses[i+1:], i+1):
                sessions2 = self.course_sessions_df[self.course_sessions_df['course_id'] == course2['course_id']]
                conflict_details = self.sessions_overlap(sessions1, sessions2)
                if conflict_details:
                    overlaps.append({
                        'course1': course1,
                        'course2': course2,
                        'conflict_type': 'time_overlap',
                        'conflicts': conflict_details
                    })
        
        return overlaps
    
    def sessions_overlap(self, sessions1, sessions2):
        """Check if any sessions between two courses overlap and return conflict details"""
        conflicts = []
        for _, session1 in sessions1.iterrows():
            for _, session2 in sessions2.iterrows():
                if session1['date'] == session2['date']:
                    start1 = parser.parse(session1['start_time']).time()
                    end1 = parser.parse(session1['end_time']).time()
                    start2 = parser.parse(session2['start_time']).time()
                    end2 = parser.parse(session2['end_time']).time()
                    if start1 < end2 and start2 < end1:
                        conflicts.append({
                            'date': session1['date'],
                            'session1': {
                                'start_time': session1['start_time'],
                                'end_time': session1['end_time']
                            },
                            'session2': {
                                'start_time': session2['start_time'],
                                'end_time': session2['end_time']
                            }
                        })
        return conflicts if conflicts else False
    
    def get_calendar_events(self, selected_course_ids):
        """Convert selected courses to calendar events format"""
        events = []
        selected_courses = self.courses_info_df[self.courses_info_df['course_id'].isin(selected_course_ids)]
        selected_sessions = self.course_sessions_df[self.course_sessions_df['course_id'].isin(selected_course_ids)]
        
        for _, session in selected_sessions.iterrows():
            course = selected_courses[selected_courses['course_id'] == session['course_id']].iloc[0]
            # Parse date without timezone conversion to avoid day shifts
            date_obj = pd.to_datetime(session['date'], format='%Y-%m-%d')
            events.append({
                'id': course['course_id'],
                'title': f"{course['course_id']}: {course['course_name']}",
                'instructor': course['instructor'],
                'location': course['location'],
                'start_time': session['start_time'],
                'end_time': session['end_time'],
                'date': session['date'],  # Keep original date string to avoid timezone issues
                'program': course['program'],
                'day': date_obj.strftime('%A')  # Add the day of week
            })
        
        return events


# Initialize the course scheduler with error handling
try:
    scheduler = CourseScheduler()
    print("Course scheduler initialized successfully")
except Exception as e:
    print(f"Error initializing course scheduler: {e}")
    # Create a dummy scheduler with empty data
    class DummyScheduler:
        def get_programs(self):
            return ['Core Courses', 'Elective Courses', 'Other Events']
        def get_all_courses(self):
            return []
        def get_courses_by_program(self, program):
            return []
        def get_calendar_events(self, course_ids):
            return []
        def find_overlapping_courses(self, courses):
            return []
    scheduler = DummyScheduler()

@app.route('/')
def index():
    """Main page with course calendar"""
    programs = scheduler.get_programs()
    courses = scheduler.get_all_courses()
    
    # Log site visit
    log_user_activity('site_visit', {'page': 'homepage'})
    
    return render_template('index.html', programs=programs, courses=courses)

@app.route('/api/courses')
def api_courses():
    """API endpoint to get courses by program"""
    program = request.args.get('program', 'All')
    courses = scheduler.get_courses_by_program(program)
    
    # Log course browsing activity
    log_user_activity('course_browsing', {'program': program, 'course_count': len(courses)})
    
    return jsonify(courses)

@app.route('/api/calendar')
def api_calendar():
    """API endpoint to get calendar events for selected courses"""
    course_ids = request.args.getlist('courses')
    events = scheduler.get_calendar_events(course_ids)
    overlaps = []
    
    if len(course_ids) > 1:
        selected_courses = scheduler.courses_info_df[scheduler.courses_info_df['course_id'].isin(course_ids)]
        overlaps = scheduler.find_overlapping_courses(selected_courses.to_dict('records'))
    
    # Log course selection activity
    log_user_activity('course_selection', {
        'selected_courses': course_ids, 
        'course_count': len(course_ids),
        'has_overlaps': len(overlaps) > 0
    })
    
    return jsonify({
        'events': events,
        'overlaps': overlaps
    })

# Add a new route to specifically track calendar exports
@app.route('/api/track/export')
def track_export():
    """Track calendar export activity"""
    course_ids = request.args.getlist('courses')
    export_format = request.args.get('format', 'ics')
    
    # Log calendar export activity
    log_user_activity('calendar_export', {
        'exported_courses': course_ids,
        'course_count': len(course_ids),
        'format': export_format
    })
    
    return jsonify({'status': 'tracked'})

@app.route('/api/programs')
def api_programs():
    """API endpoint to get all programs"""
    programs = scheduler.get_programs()
    return jsonify(programs)

@app.route('/stats')
def view_stats():
    """View application statistics dashboard"""
    try:
        total_requests = RequestLog.query.count()
        recent_requests = RequestLog.query.order_by(RequestLog.timestamp.desc()).limit(10).all()
        
        # Basic statistics
        stats = {
            'total_requests': total_requests,
            'recent_requests': []
        }
        
        for req in recent_requests:
            stats['recent_requests'].append({
                'timestamp': req.timestamp.isoformat() if req.timestamp else None,
                'method': req.method,
                'path': req.path,
                'status_code': req.status_code,
                'response_time': req.response_time,
                'remote_addr': req.remote_addr
            })
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats/summary')
def stats_summary():
    """Get summary statistics including user activities"""
    try:
        # Request statistics
        total_requests = RequestLog.query.count()
        if total_requests == 0:
            avg_response_time = 0
            top_paths = []
            status_codes = {}
            methods = {}
        else:
            from sqlalchemy import func
            avg_response_time = db.session.query(func.avg(RequestLog.response_time)).scalar() or 0
            
            # Top requested paths
            top_paths = db.session.query(
                RequestLog.path, 
                func.count(RequestLog.path).label('count')
            ).group_by(RequestLog.path).order_by(func.count(RequestLog.path).desc()).limit(5).all()
            
            # Status code distribution
            status_codes_query = db.session.query(
                RequestLog.status_code,
                func.count(RequestLog.status_code).label('count')
            ).group_by(RequestLog.status_code).all()
            
            # HTTP methods distribution
            methods_query = db.session.query(
                RequestLog.method,
                func.count(RequestLog.method).label('count')
            ).group_by(RequestLog.method).all()
            
            status_codes = {str(code): count for code, count in status_codes_query}
            methods = {method: count for method, count in methods_query}
        
        # User activity statistics
        total_activities = UserActivity.query.count()
        site_visits = UserActivity.query.filter_by(activity_type='site_visit').count()
        calendar_exports = UserActivity.query.filter_by(activity_type='calendar_export').count()
        course_selections = UserActivity.query.filter_by(activity_type='course_selection').count()
        course_browsing = UserActivity.query.filter_by(activity_type='course_browsing').count()
        
        # Activity distribution
        from sqlalchemy import func
        activity_distribution = db.session.query(
            UserActivity.activity_type,
            func.count(UserActivity.activity_type).label('count')
        ).group_by(UserActivity.activity_type).all()
        
        # Recent activities
        recent_activities = UserActivity.query.order_by(UserActivity.timestamp.desc()).limit(10).all()
        
        return jsonify({
            'total_requests': total_requests,
            'avg_response_time': round(avg_response_time, 3),
            'top_paths': [{'path': path, 'count': count} for path, count in top_paths],
            'status_codes': status_codes,
            'methods': methods,
            'user_activities': {
                'total_activities': total_activities,
                'site_visits': site_visits,
                'calendar_exports': calendar_exports,
                'course_selections': course_selections,
                'course_browsing': course_browsing,
                'activity_distribution': {activity: count for activity, count in activity_distribution},
                'recent_activities': [{
                    'timestamp': activity.timestamp.isoformat() if activity.timestamp else None,
                    'type': activity.activity_type,
                    'details': json.loads(activity.details) if activity.details else None,
                    'remote_addr': activity.remote_addr
                } for activity in recent_activities]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats/dashboard')
def stats_dashboard():
    """Render a simple HTML dashboard for statistics"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Application Statistics</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .stat-card { 
                background: #f5f5f5; 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 5px; 
                border-left: 4px solid #007bff;
            }
            .activity-card {
                background: #e8f5e8;
                border-left: 4px solid #28a745;
            }
            .stat-value { font-size: 2em; font-weight: bold; color: #007bff; }
            .activity-value { font-size: 2em; font-weight: bold; color: #28a745; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
            .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .full-width { grid-column: 1 / -1; }
        </style>
    </head>
    <body>
        <h1>MBA Course Schedule Manager - Analytics Dashboard</h1>
        <div id="stats-container">Loading...</div>
        
        <script>
            fetch('/stats/summary')
                .then(response => response.json())
                .then(data => {
                    const activities = data.user_activities || {};
                    document.getElementById('stats-container').innerHTML = `
                        <div class="dashboard-grid">
                            <div class="stat-card">
                                <h3>Total HTTP Requests</h3>
                                <div class="stat-value">${data.total_requests}</div>
                            </div>
                            <div class="stat-card">
                                <h3>Average Response Time</h3>
                                <div class="stat-value">${data.avg_response_time}ms</div>
                            </div>
                            <div class="stat-card activity-card">
                                <h3>Site Visits</h3>
                                <div class="activity-value">${activities.site_visits || 0}</div>
                            </div>
                            <div class="stat-card activity-card">
                                <h3>Calendar Exports</h3>
                                <div class="activity-value">${activities.calendar_exports || 0}</div>
                            </div>
                            <div class="stat-card activity-card">
                                <h3>Course Selections</h3>
                                <div class="activity-value">${activities.course_selections || 0}</div>
                            </div>
                            <div class="stat-card activity-card">
                                <h3>Course Browsing</h3>
                                <div class="activity-value">${activities.course_browsing || 0}</div>
                            </div>
                        </div>
                        
                        <div class="stat-card full-width">
                            <h3>User Activity Distribution</h3>
                            <table>
                                <tr><th>Activity Type</th><th>Count</th></tr>
                                ${Object.entries(activities.activity_distribution || {}).map(([activity, count]) => 
                                    `<tr><td>${activity.replace('_', ' ').toUpperCase()}</td><td>${count}</td></tr>`
                                ).join('')}
                            </table>
                        </div>
                        
                        <div class="stat-card full-width">
                            <h3>Top Requested Paths</h3>
                            <table>
                                <tr><th>Path</th><th>Count</th></tr>
                                ${data.top_paths.map(item => `<tr><td>${item.path}</td><td>${item.count}</td></tr>`).join('')}
                            </table>
                        </div>
                        
                        <div class="dashboard-grid">
                            <div class="stat-card">
                                <h3>HTTP Status Codes</h3>
                                <table>
                                    <tr><th>Code</th><th>Count</th></tr>
                                    ${Object.entries(data.status_codes).map(([code, count]) => 
                                        `<tr><td>${code}</td><td>${count}</td></tr>`
                                    ).join('')}
                                </table>
                            </div>
                            <div class="stat-card">
                                <h3>HTTP Methods</h3>
                                <table>
                                    <tr><th>Method</th><th>Count</th></tr>
                                    ${Object.entries(data.methods).map(([method, count]) => 
                                        `<tr><td>${method}</td><td>${count}</td></tr>`
                                    ).join('')}
                                </table>
                            </div>
                        </div>
                        
                        <div class="stat-card full-width">
                            <h3>Recent User Activities</h3>
                            <table>
                                <tr><th>Time</th><th>Activity</th><th>Details</th><th>IP Address</th></tr>
                                ${(activities.recent_activities || []).map(activity => `
                                    <tr>
                                        <td>${new Date(activity.timestamp).toLocaleString()}</td>
                                        <td>${activity.type.replace('_', ' ').toUpperCase()}</td>
                                        <td>${activity.details ? JSON.stringify(activity.details) : 'N/A'}</td>
                                        <td>${activity.remote_addr}</td>
                                    </tr>
                                `).join('')}
                            </table>
                        </div>
                    `;
                })
                .catch(error => {
                    document.getElementById('stats-container').innerHTML = 'Error loading statistics: ' + error;
                });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
