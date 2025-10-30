# Home Storage Product Tracker - Code Overview

## Overview

This is a Flask-based web application designed to help users track and manage their home storage inventory. Users can organize storage items (primarily food products) across different physical locations with detailed tracking of expiration dates, nutritional information, and ingredients.

## Purpose

The application solves the problem of tracking what items you have stored in various locations around your home (pantry, garage, freezer, etc.) and helps prevent waste by monitoring expiration dates. Each user has their own isolated inventory, making it suitable for multi-user households or deployments.

## Technology Stack

### Backend
- **Flask 3.1.1** - Python web framework
- **MongoDB** - NoSQL document database for flexible data storage
- **flask-pymongo** - MongoDB integration
- **Authlib** - Google OAuth 2.0 authentication
- **python-dotenv** - Environment configuration management

### Frontend
- **Bootstrap 5.3.2** - Responsive UI framework
- **Jinja2** - Server-side templating
- **Vanilla JavaScript** - Dark/light theme toggling

### DevOps
- **Docker & docker-compose** - Containerization and orchestration
- **Mongo Express** - Web-based MongoDB administration interface

## Key Features

### 1. Google OAuth Authentication
- Secure login using Google SSO
- User session management
- Multi-tenant data isolation
- Optional demo mode for testing (`USE_AUTH=false`)

### 2. Location Management
- Create, view, edit, and delete storage locations
- Each location has a name and description
- Examples: "Pantry", "Garage Shelf", "Basement Freezer"

### 3. Storage Item Management
- Comprehensive item tracking with the following fields:
  - Name and brand
  - Size/quantity
  - Nutritional information
  - Purchase date
  - Expiration date
  - Ingredients list
  - Additional notes
  - Associated storage location

### 4. User Interface
- Responsive design that works on mobile and desktop
- Dark/light mode with localStorage persistence
- Flash messages for user feedback
- Clean table-based listings
- Form validation

## Project Structure

```
storage-python/
├── app.py                          # Main Flask application (17 routes)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container configuration
├── docker-compose.yml              # Multi-container orchestration
├── entrypoint.sh                   # Docker startup script
├── insert_sample_data.py           # Demo data generator
├── reset_mongo_collections.py     # Database reset utility
├── .env / .env.docker              # Environment configuration
├── static/
│   ├── styles.css                  # Custom dark mode styles
│   └── theme.js                    # Theme toggle logic
└── templates/
    ├── base.html                   # Base template with navbar
    ├── index.html                  # Home page
    ├── locations.html              # Location list
    ├── location_form.html          # Add/edit location
    ├── location_view.html          # Location details
    ├── items.html                  # Items list
    ├── item_form.html              # Add/edit item
    └── item_view.html              # Item details
```

## Database Schema

### Collections

**users**
- `_id`: String (Google sub ID or email)
- `email`: User's email address
- `name`: User's display name

**locations** (indexed on `user_id`)
- `_id`: ObjectId
- `name`: Location name
- `description`: Location description
- `user_id`: Owner reference

**storage_items** (indexed on `user_id` and `location_id`)
- `_id`: ObjectId
- `name`: Item name
- `brand`: Brand name
- `size`: Size/quantity
- `nutritional_info`: Nutritional details
- `date_purchased`: Purchase date (YYYY-MM-DD)
- `expiration_date`: Expiration date (YYYY-MM-DD)
- `ingredients`: Ingredients list
- `other_info`: Additional notes
- `location_id`: Location reference
- `user_id`: Owner reference

## Application Routes

### Authentication (`app.py`)
- `GET /` - Home page
- `GET /login` - Initiate Google OAuth or demo login
- `GET /login/authorized` - OAuth callback handler
- `GET /logout` - Clear session and logout

### Locations (all require authentication)
- `GET /locations` - List all user's locations
- `GET /locations/add` - Show add location form
- `POST /locations/add` - Create new location
- `GET /locations/<id>` - View location details
- `GET /locations/<id>/edit` - Show edit form
- `POST /locations/<id>/edit` - Update location
- `POST /locations/<id>/delete` - Delete location

### Items (all require authentication)
- `GET /items` - List all user's items
- `GET /items/add` - Show add item form
- `POST /items/add` - Create new item
- `GET /items/<id>` - View item details
- `GET /items/<id>/edit` - Show edit form
- `POST /items/<id>/edit` - Update item
- `POST /items/<id>/delete` - Delete item

## Security Features

1. **Google OAuth 2.0** - Industry-standard authentication
2. **Session-based Authorization** - Encrypted Flask sessions
3. **Multi-tenant Isolation** - All queries filtered by `user_id`
4. **Environment Variables** - Secrets kept out of code
5. **MongoDB Authentication** - Database access control

## Docker Deployment

The application includes a complete Docker setup with three services:

1. **mongo** - MongoDB 6 with authentication
2. **flask** - Python application server
3. **mongo-express** - Database admin UI (http://localhost:8081)

Start with: `docker-compose up`

The Flask app runs on http://localhost:5000

## Utility Scripts

### insert_sample_data.py
Populates the database with demo data including:
- Multiple demo users
- Sample locations (pantry, garage, basement)
- Sample storage items with realistic data

Useful for testing and development.

### reset_mongo_collections.py
Drops and recreates all collections with proper indexes. Use this to reset the database to a clean state during development.

## Development Workflow

1. **Local Development**:
   - Set up `.env` with Google OAuth credentials and MongoDB URI
   - Install dependencies: `pip install -r requirements.txt`
   - Run: `python app.py`

2. **Docker Development**:
   - Configure `.env.docker`
   - Run: `docker-compose up`
   - Access Mongo Express at http://localhost:8081

3. **Database Management**:
   - Reset collections: `python reset_mongo_collections.py`
   - Insert sample data: `python insert_sample_data.py`

## Configuration

### Environment Variables

**Required:**
- `SECRET_KEY` - Flask session encryption key
- `MONGO_URI` - MongoDB connection string
- `GOOGLE_CLIENT_ID` - OAuth client ID
- `GOOGLE_CLIENT_SECRET` - OAuth client secret

**Optional:**
- `USE_AUTH` - Set to "false" to disable Google login (demo mode)

## Template Architecture

All templates extend `base.html`, which provides:
- Bootstrap CSS/JS framework
- Navigation bar with conditional login/logout
- Dark/light theme toggle button
- Flash message display area
- Responsive container layout

This promotes DRY principles and consistent UI across all pages.

## Current Development Branch

According to git status, the current branch is `feature/add-docker`, which suggests ongoing work to add or improve Docker support. Recent changes include:
- Modified `.gitignore` and `requirements.txt`
- New untracked files: `Dockerfile`, `docker-compose.yml`, `entrypoint.sh`

## Code Quality Highlights

- **Separation of Concerns**: Clear separation between routes, database operations, and templates
- **User Data Isolation**: All queries properly scoped to authenticated user
- **Reusable Templates**: Base template with block inheritance
- **Comprehensive CRUD**: Full create/read/update/delete for all entities
- **Error Handling**: Flash messages provide user feedback
- **Development Tools**: Sample data and reset scripts included

## Future Enhancement Considerations

While the application is functional, potential improvements could include:
- CSRF token protection (Flask-WTF)
- Server-side delete confirmations
- Expiration date alerts/notifications
- Search and filter functionality
- Bulk operations
- Export/import features
- Mobile app or PWA support
- Rate limiting on API endpoints
- Enhanced session security (httponly, secure flags)

---

**Last Updated**: 2025-10-28
**Repository**: C:\git\Reinowned\Code Samples\storage-python
