# Course Schedule Manager

A dynamic Flask web application for managing course schedules with visual calendar interface and conflict detection.

## Features

- **Dynamic Calendar**: Visual weekly schedule showing selected courses
- **Program Filters**: Filter courses by academic program
- **Course Selection**: Interactive course selection with real-time updates
- **Conflict Detection**: Automatically detects and highlights overlapping courses
- **Responsive Design**: Works on desktop and mobile devices
- **Azure Ready**: Configured for Microsoft Azure deployment

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## Azure Deployment

This application is configured for Azure App Service deployment:

1. Create an Azure App Service instance
2. Deploy using Git or GitHub Actions
3. The application will run on the assigned Azure URL

## Course Data

Course information is stored in `courses.csv` with the following columns:
- course_id: Unique course identifier
- course_name: Full course name
- instructor: Course instructor
- start_date/end_date: Course duration
- start_time/end_time: Daily class times
- days: Days of the week (comma-separated)
- location: Classroom/lab location
- credits: Credit hours
- program: Academic program

## API Endpoints

- `/api/courses?program=<program>`: Get courses by program
- `/api/calendar?courses=<course_ids>`: Get calendar events for selected courses
- `/api/programs`: Get all available programs

## Usage

1. Open the application in your web browser
2. Use the program filter to narrow down course options
3. Click on courses to add/remove them from your schedule
4. View your schedule in the weekly calendar
5. Check for time conflicts in the warnings section

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, JavaScript
- **Data**: Pandas for CSV processing
- **Deployment**: Gunicorn for Azure App Service
