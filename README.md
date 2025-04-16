# Tourism Ireland Attraction Management System

A web-based information system for Tourism Ireland to manage and showcase tourist attractions across the island of Ireland. The application provides comprehensive CRUD (Create, Read, Update, Delete) functionality for tourist attractions via a Python Flask API with an attractive Bootstrap-styled frontend.

## Features

- **Modern UI**: Attractive, responsive design with Irish-themed styling
- **CRUD Operations**: Full create, read, update, and delete capabilities for attractions
- **Search Functionality**: Search attractions by name, location, or description
- **Sorting**: Sort attractions by various attributes in ascending or descending order
- **Data Validation**: Client and server-side validation for data integrity
- **Responsive Design**: Mobile-friendly interface that works on devices of all sizes
- **Interactive Components**: Dynamic content updates without page reloads
- **Image Integration**: Display attraction images for visual appeal
- **External Links**: Direct links to attraction websites

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **CSS Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Data Storage**: JSON file-based storage
- **API**: RESTful API architecture

## Project Structure

```
tourism-ireland/
├── data/
│   └── attractions.json       # JSON data storage
├── static/
│   ├── css/
│   │   └── styles.css         # Custom styles
│   └── js/
│       ├── api.js             # API service
│       ├── main.js            # Main application logic
│       └── validation.js      # Form validation
├── templates/
│   ├── index.html             # Main page template
│   └── layout.html            # Base layout template
├── tests/
│   ├── test_api.py            # API unit tests
│   └── test_integration.py    # Integration tests
├── app.py                     # Flask application
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## API Endpoints

- `GET /api/attractions`: Get all attractions with optional search and sort parameters
- `GET /api/attractions/<id>`: Get a specific attraction by ID
- `POST /api/attractions`: Create a new attraction
- `PUT /api/attractions/<id>`: Update an existing attraction
- `DELETE /api/attractions/<id>`: Delete an attraction

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r project-requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```
   or with Gunicorn:
   ```
   gunicorn --bind 0.0.0.0:5000 main:app
   ```
4. Open your browser and navigate to `http://localhost:5000`

## Required Environment Variables

- `SESSION_SECRET`: Secret key for session management (optional, defaults to a development key)

## Development

### Running Tests

```
pytest
```

### Adding New Attractions

Use the "Add Attraction" button in the UI or make a POST request to the API endpoint.

## About Tourism Ireland

Tourism Ireland is responsible for marketing the island of Ireland overseas as a holiday and business tourism destination. Their remit is to increase tourism to the island of Ireland and to support Northern Ireland to realize its tourism potential.

They operate under the auspices of the North South Ministerial Council through the Department for the Economy in Northern Ireland and the Department of Enterprise, Tourism and Employment in Ireland.

## License

This project is developed for educational purposes. All rights reserved.
