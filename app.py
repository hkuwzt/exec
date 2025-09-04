from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
from datetime import datetime, timedelta
from dateutil import parser
import os

app = Flask(__name__)

class CourseScheduler:
    def __init__(self, csv_file='courses.csv'):
        self.csv_file = csv_file
        self.courses_df = self.load_courses()
    
    def load_courses(self):
        """Load courses from CSV file"""
        try:
            df = pd.read_csv(self.csv_file)
            # Convert time strings to datetime objects for comparison
            df['start_datetime'] = pd.to_datetime(df['start_date'] + ' ' + df['start_time'])
            df['end_datetime'] = pd.to_datetime(df['start_date'] + ' ' + df['end_time'])
            return df
        except FileNotFoundError:
            # Create sample data if CSV doesn't exist
            return self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample course data"""
        sample_data = {
            'course_id': ['CS101', 'CS102', 'CS103', 'MATH201', 'MATH202', 'ENG101', 'PHYS101', 'CS201'],
            'course_name': [
                'Introduction to Programming',
                'Data Structures',
                'Web Development',
                'Calculus I',
                'Linear Algebra',
                'Technical Writing',
                'Physics I',
                'Advanced Programming'
            ],
            'instructor': [
                'Dr. Smith',
                'Prof. Johnson',
                'Dr. Brown',
                'Dr. Wilson',
                'Prof. Davis',
                'Ms. Garcia',
                'Dr. Lee',
                'Dr. Smith'
            ],
            'start_date': [
                '2025-09-01', '2025-09-01', '2025-09-01', '2025-09-01',
                '2025-09-01', '2025-09-01', '2025-09-01', '2025-09-01'
            ],
            'end_date': [
                '2025-12-15', '2025-12-15', '2025-12-15', '2025-12-15',
                '2025-12-15', '2025-12-15', '2025-12-15', '2025-12-15'
            ],
            'start_time': [
                '09:00', '11:00', '14:00', '10:00',
                '13:00', '15:00', '09:00', '16:00'
            ],
            'end_time': [
                '10:30', '12:30', '15:30', '11:30',
                '14:30', '16:30', '10:30', '17:30'
            ],
            'days': [
                'Monday,Wednesday,Friday',
                'Tuesday,Thursday',
                'Monday,Wednesday',
                'Monday,Wednesday,Friday',
                'Tuesday,Thursday',
                'Wednesday,Friday',
                'Tuesday,Thursday',
                'Monday,Wednesday,Friday'
            ],
            'location': [
                'Room 101', 'Room 102', 'Lab 201', 'Room 103',
                'Room 104', 'Room 105', 'Lab 301', 'Lab 202'
            ],
            'credits': [3, 4, 3, 4, 3, 2, 4, 3],
            'program': [
                'Computer Science', 'Computer Science', 'Computer Science', 'Mathematics',
                'Mathematics', 'General Education', 'Physics', 'Computer Science'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        df['start_datetime'] = pd.to_datetime(df['start_date'] + ' ' + df['start_time'])
        df['end_datetime'] = pd.to_datetime(df['start_date'] + ' ' + df['end_time'])
        
        # Save sample data to CSV
        df.to_csv(self.csv_file, index=False)
        return df
    
    def get_all_courses(self):
        """Return all courses as a list of dictionaries"""
        return self.courses_df.to_dict('records')
    
    def get_courses_by_program(self, program):
        """Filter courses by program"""
        if program == 'All':
            return self.get_all_courses()
        filtered_df = self.courses_df[self.courses_df['program'] == program]
        return filtered_df.to_dict('records')
    
    def get_programs(self):
        """Get all unique programs"""
        return sorted(self.courses_df['program'].unique().tolist())
    
    def find_overlapping_courses(self, selected_courses):
        """Find courses that have time conflicts"""
        overlaps = []
        
        for i, course1 in enumerate(selected_courses):
            for j, course2 in enumerate(selected_courses[i+1:], i+1):
                if self.courses_overlap(course1, course2):
                    overlaps.append({
                        'course1': course1,
                        'course2': course2,
                        'conflict_type': 'time_overlap'
                    })
        
        return overlaps
    
    def courses_overlap(self, course1, course2):
        """Check if two courses have overlapping times"""
        # Check if they share any days
        days1 = set(course1['days'].split(','))
        days2 = set(course2['days'].split(','))
        
        if not days1.intersection(days2):
            return False
        
        # Check time overlap
        start1 = parser.parse(course1['start_time']).time()
        end1 = parser.parse(course1['end_time']).time()
        start2 = parser.parse(course2['start_time']).time()
        end2 = parser.parse(course2['end_time']).time()
        
        return start1 < end2 and start2 < end1
    
    def get_calendar_events(self, selected_course_ids):
        """Convert selected courses to calendar events format"""
        events = []
        selected_courses = self.courses_df[self.courses_df['course_id'].isin(selected_course_ids)]
        
        for _, course in selected_courses.iterrows():
            days = course['days'].split(',')
            
            # Generate events for each day of the week
            for day in days:
                day = day.strip()
                events.append({
                    'id': course['course_id'],
                    'title': f"{course['course_id']}: {course['course_name']}",
                    'instructor': course['instructor'],
                    'location': course['location'],
                    'start_time': course['start_time'],
                    'end_time': course['end_time'],
                    'day': day,
                    'credits': course['credits'],
                    'program': course['program']
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
        selected_courses = scheduler.courses_df[scheduler.courses_df['course_id'].isin(course_ids)]
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
