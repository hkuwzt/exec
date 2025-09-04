# Course Schedule Manager - Complete Documentation

## Overview
This Flask web application provides a dynamic course scheduling system with visual calendar interface, designed for deployment on Microsoft Azure. The application allows students and administrators to manage course schedules, detect conflicts, and visualize weekly timetables.

## Features Implemented

### ✅ Dynamic Calendar
- **Weekly Grid View**: Shows courses in a time-slot grid format
- **Real-time Updates**: Calendar updates immediately when courses are selected/deselected
- **Visual Course Blocks**: Each course appears as a colored block with course ID
- **Hover Information**: Shows detailed course info on hover
- **Time Slots**: Covers 8 AM to 6 PM academic hours

### ✅ Course Filtering System
- **Program Filter**: Dropdown to filter courses by academic program
- **Real-time Filtering**: Course list updates instantly when filter changes
- **Multiple Programs**: Supports Computer Science, Mathematics, Physics, General Education
- **"All Programs" Option**: Shows all available courses

### ✅ Interactive Course Selection
- **Click to Select/Deselect**: Simple click interface for course management
- **Visual Feedback**: Selected courses highlighted with different styling
- **Course Cards**: Each course displayed with comprehensive information:
  - Course ID and name
  - Instructor
  - Time schedule
  - Days of week
  - Location
  - Credit hours
  - Academic program

### ✅ Overlap Detection and Visualization
- **Automatic Detection**: System automatically finds time conflicts
- **Visual Warnings**: Conflicting courses highlighted in red with pulsing animation
- **Detailed Conflict Reports**: Shows which specific courses conflict
- **Real-time Updates**: Conflict detection runs whenever course selection changes

### ✅ CSV-based Course Data
- **Structured Data**: All course information stored in `courses.csv`
- **Easy Updates**: Simply edit CSV file to add/modify courses
- **Comprehensive Fields**: Includes all necessary course attributes
- **Sample Data**: Comes with realistic sample course data

### ✅ Azure-Ready Deployment
- **Gunicorn Configuration**: Production-ready WSGI server
- **Environment Variables**: Port configuration for Azure
- **Requirements File**: All dependencies properly listed
- **Deployment Scripts**: Multiple deployment options provided

## File Structure
```
workshop/
├── app.py                  # Main Flask application
├── courses.csv            # Course data (easily editable)
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku/Azure deployment config
├── startup.sh            # Azure startup script
├── test_app.py           # Test script
├── README.md             # Basic documentation
├── AZURE_DEPLOYMENT.md   # Detailed deployment guide
├── azure-deploy.json     # Azure ARM template
├── .gitignore           # Git ignore rules
├── templates/
│   └── index.html       # Main web interface
└── .github/
    └── workflows/
        └── azure-deploy.yml  # GitHub Actions deployment
```

## Technical Architecture

### Backend (Flask/Python)
- **CourseScheduler Class**: Core business logic
- **CSV Processing**: Pandas for data manipulation
- **Date/Time Handling**: python-dateutil for time parsing
- **REST API**: JSON endpoints for frontend communication
- **Conflict Detection**: Algorithm to find overlapping courses

### Frontend (HTML/CSS/JavaScript)
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icons for better UX
- **Vanilla JavaScript**: No framework dependencies
- **AJAX Communication**: Async API calls
- **CSS Grid**: Calendar layout system

### Data Model
```csv
course_id,course_name,instructor,start_date,end_date,start_time,end_time,days,location,credits,program
```

## API Endpoints

### GET `/api/courses?program=<program>`
Returns courses filtered by program
```json
[
  {
    "course_id": "CS101",
    "course_name": "Introduction to Programming",
    "instructor": "Dr. Smith",
    "start_time": "09:00",
    "end_time": "10:30",
    "days": "Monday,Wednesday,Friday",
    "location": "Room 101",
    "credits": 3,
    "program": "Computer Science"
  }
]
```

### GET `/api/calendar?courses=CS101&courses=CS102`
Returns calendar events and overlaps for selected courses
```json
{
  "events": [...],
  "overlaps": [
    {
      "course1": {...},
      "course2": {...},
      "conflict_type": "time_overlap"
    }
  ]
}
```

### GET `/api/programs`
Returns all available programs
```json
["Computer Science", "Mathematics", "Physics", "General Education"]
```

## Azure Deployment Options

### 1. Azure Portal (Recommended for beginners)
- Use Web App creation wizard
- Connect to GitHub repository
- Automatic deployment on push

### 2. Azure CLI (For developers)
- Script-based deployment
- Full control over configuration
- Suitable for CI/CD pipelines

### 3. GitHub Actions (For automated deployment)
- Automatic deployment on code changes
- Includes testing pipeline
- Professional development workflow

### 4. VS Code Extension (For quick deployment)
- Right-click deployment
- Integrated development experience
- Good for rapid prototyping

## Configuration for Azure

The application is pre-configured for Azure with:
- **Port Binding**: Uses `PORT` environment variable
- **Host Configuration**: Binds to `0.0.0.0` for Azure compatibility
- **Gunicorn Setup**: Production WSGI server configuration
- **Static Files**: Proper static file handling

## Customization Guide

### Adding New Courses
Edit `courses.csv` and add new rows with required fields:
```csv
CS401,Advanced Algorithms,Dr. Johnson,2025-09-01,2025-12-15,14:00,15:30,"Tuesday,Thursday",Lab 301,4,Computer Science
```

### Modifying Time Slots
In `templates/index.html`, update the `timeSlots` array:
```javascript
for (let hour = 7; hour <= 22; hour++) {  // Extend to 10 PM
    timeSlots.push(`${hour.toString().padStart(2, '0')}:00`);
}
```

### Adding New Programs
Simply add courses with new program names in the CSV - the system automatically detects unique programs.

### Styling Changes
Modify CSS in `templates/index.html` or create separate CSS files in a `static/` directory.

## Security Considerations

- **Input Validation**: All user inputs are validated
- **HTTPS**: Azure provides SSL/TLS automatically
- **Environment Variables**: Sensitive data should use Azure App Settings
- **CORS**: Configure if API access needed from other domains

## Performance Optimizations

- **CSV Caching**: Course data loaded once at startup
- **Minimal Dependencies**: Only essential packages included
- **Client-side Processing**: Calendar rendering done in browser
- **Efficient Algorithms**: O(n²) conflict detection is acceptable for typical course loads

## Troubleshooting

### Common Issues:
1. **Port Binding**: Ensure app uses `PORT` environment variable
2. **Static Files**: Check file paths are correct for Azure
3. **CSV Format**: Verify CSV has proper headers and data types
4. **Time Parsing**: Ensure time format is HH:MM (24-hour)

### Debug Mode:
Set `debug=False` for production deployment on Azure.

## Future Enhancements

Potential improvements:
- **Database Integration**: Replace CSV with PostgreSQL/MySQL
- **User Authentication**: Add login system
- **Course Registration**: Allow actual enrollment
- **Email Notifications**: Send conflict alerts
- **Mobile App**: React Native companion app
- **Advanced Filtering**: Search by instructor, time, location
- **Export Features**: PDF/iCal export of schedules
- **Room Availability**: Integration with facility management

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Azure deployment logs
3. Verify CSV data format
4. Test locally before deploying

The application is designed to be maintainable, scalable, and easy to deploy on Microsoft Azure.
