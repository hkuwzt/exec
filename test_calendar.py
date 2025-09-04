#!/usr/bin/env python3
"""
Quick test script to verify calendar functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import scheduler

def test_calendar_events():
    print("=== Testing Calendar Events Generation ===\n")
    
    # Test with a single course
    print("1. Testing CS101 (Monday, Wednesday, Friday):")
    events = scheduler.get_calendar_events(['CS101'])
    for event in events:
        print(f"   {event['day']}: {event['start_time']}-{event['end_time']} - {event['id']}")
    print(f"   Total events: {len(events)}")
    
    print("\n2. Testing CS102 (Tuesday, Thursday):")
    events = scheduler.get_calendar_events(['CS102'])
    for event in events:
        print(f"   {event['day']}: {event['start_time']}-{event['end_time']} - {event['id']}")
    print(f"   Total events: {len(events)}")
    
    print("\n3. Testing multiple courses (CS101, CS102):")
    events = scheduler.get_calendar_events(['CS101', 'CS102'])
    for event in events:
        print(f"   {event['day']}: {event['start_time']}-{event['end_time']} - {event['id']}")
    print(f"   Total events: {len(events)}")
    
    print("\n4. Testing overlap detection:")
    courses = scheduler.courses_df[scheduler.courses_df['course_id'].isin(['CS101', 'PHYS101'])]
    overlaps = scheduler.find_overlapping_courses(courses.to_dict('records'))
    if overlaps:
        for overlap in overlaps:
            print(f"   Conflict: {overlap['course1']['course_id']} vs {overlap['course2']['course_id']}")
    else:
        print("   No conflicts detected")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_calendar_events()
