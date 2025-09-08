from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
from datetime import datetime, timedelta
from dateutil import parser
import os

app = Flask(__name__)

class CourseScheduler:
    def __init__(self, courses_info='courses_info.csv', course_sessions='course_sessions.csv'):
        self.courses_info_file = courses_info
        self.course_sessions_file = course_sessions
        self.courses_info_df = self.load_courses_info()
        self.course_sessions_df = self.load_course_sessions()
    
    def load_courses_info(self):
        """Load basic course information from CSV file"""
        try:
            return pd.read_csv(self.courses_info_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Course information file {self.courses_info_file} not found")
    
    def load_course_sessions(self):
        """Load course sessions from CSV file"""
        try:
            df = pd.read_csv(self.course_sessions_file)
            df['start_datetime'] = pd.to_datetime(df['date'] + ' ' + df['start_time'])
            df['end_datetime'] = pd.to_datetime(df['date'] + ' ' + df['end_time'])
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"Course sessions file {self.course_sessions_file} not found")
    
    def get_all_courses(self):
        """Return all courses as a list of dictionaries"""
        return self.courses_info_df.to_dict('records')
    
    def get_courses_by_program(self, program):
        """Filter courses by program"""
        if program == 'All':
            return self.get_all_courses()
        filtered_df = self.courses_info_df[self.courses_info_df['program'] == program]
        return filtered_df.to_dict('records')
    
    def get_programs(self):
        """Get all unique programs"""
        return sorted(self.courses_info_df['program'].unique().tolist())
    
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
            date_obj = pd.to_datetime(session['date'])
            events.append({
                'id': course['course_id'],
                'title': f"{course['course_id']}: {course['course_name']}",
                'instructor': course['instructor'],
                'location': course['location'],
                'start_time': session['start_time'],
                'end_time': session['end_time'],
                'date': session['date'],
                'program': course['program'],
                'day': date_obj.strftime('%A')  # Add the day of week
            })
        
        return events


# Initialize the course scheduler
scheduler = CourseScheduler()

@app.route('/')
def index():
    """Main page with course calendar"""
    programs = scheduler.get_programs()
    courses = scheduler.get_all_courses()
    return render_template('index.html', programs=programs, courses=courses)

@app.route('/api/courses')
def api_courses():
    """API endpoint to get courses by program"""
    program = request.args.get('program', 'All')
    courses = scheduler.get_courses_by_program(program)
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
    
    return jsonify({
        'events': events,
        'overlaps': overlaps
    })

@app.route('/api/programs')
def api_programs():
    """API endpoint to get all programs"""
    programs = scheduler.get_programs()
    return jsonify(programs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
