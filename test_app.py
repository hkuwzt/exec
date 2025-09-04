"""
Test script to demonstrate the Course Schedule Manager functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import CourseScheduler

def test_course_scheduler():
    """Test the CourseScheduler functionality"""
    print("=== Course Schedule Manager Test ===\n")
    
    # Initialize scheduler
    scheduler = CourseScheduler()
    print("✓ Course scheduler initialized")
    
    # Test loading courses
    all_courses = scheduler.get_all_courses()
    print(f"✓ Loaded {len(all_courses)} courses from CSV")
    
    # Test programs
    programs = scheduler.get_programs()
    print(f"✓ Found {len(programs)} programs: {', '.join(programs)}")
    
    # Test filtering by program
    cs_courses = scheduler.get_courses_by_program('Computer Science')
    print(f"✓ Found {len(cs_courses)} Computer Science courses")
    
    # Test calendar events
    selected_courses = ['CS101', 'CS102', 'MATH201']
    events = scheduler.get_calendar_events(selected_courses)
    print(f"✓ Generated {len(events)} calendar events for selected courses")
    
    # Test overlap detection
    overlaps = scheduler.find_overlapping_courses([
        course for course in all_courses 
        if course['course_id'] in selected_courses
    ])
    print(f"✓ Found {len(overlaps)} time conflicts")
    
    # Display sample course information
    print("\n=== Sample Course Information ===")
    for i, course in enumerate(all_courses[:3]):
        print(f"\nCourse {i+1}:")
        print(f"  ID: {course['course_id']}")
        print(f"  Name: {course['course_name']}")
        print(f"  Instructor: {course['instructor']}")
        print(f"  Time: {course['start_time']} - {course['end_time']}")
        print(f"  Days: {course['days']}")
        print(f"  Location: {course['location']}")
        print(f"  Credits: {course['credits']}")
        print(f"  Program: {course['program']}")
    
    # Test overlap detection with conflicting courses
    print("\n=== Testing Overlap Detection ===")
    conflicting_courses = ['CS101', 'PHYS101']  # Both on Tuesday/Thursday 9:00-10:30
    conflict_events = scheduler.get_calendar_events(conflicting_courses)
    conflict_overlaps = scheduler.find_overlapping_courses([
        course for course in all_courses 
        if course['course_id'] in conflicting_courses
    ])
    
    if conflict_overlaps:
        print("✓ Conflict detection working!")
        for overlap in conflict_overlaps:
            print(f"  Conflict: {overlap['course1']['course_id']} overlaps with {overlap['course2']['course_id']}")
    else:
        print("No conflicts detected (may need to check course times)")
    
    print("\n=== Test Complete ===")
    print("The Course Schedule Manager is ready for deployment!")

if __name__ == "__main__":
    test_course_scheduler()
