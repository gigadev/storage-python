# Storage Tracker - Complete Project Summary

## Project Overview

This repository contains a complete full-stack home storage tracking solution with:

1. **Flask Web Application** (Python)
2. **.NET MAUI Mobile App** (C#/Blazor Hybrid)
3. **MongoDB Database** (NoSQL)
4. **Docker Infrastructure** (Containerization)

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Google OAuth 2.0                      │
│                   (Authentication)                        │
└───────────────────┬──────────────────────────────────────┘
                    │
        ┌───────────┴──────────────┐
        │                          │
┌───────▼────────┐        ┌────────▼─────────┐
│  Web Browser   │        │   Mobile App     │
│  (Flask UI)    │        │  (.NET MAUI)     │
└───────┬────────┘        └────────┬─────────┘
        │                          │
        │                  ┌───────▼─────────┐
        │                  │  Local SQLite   │
        │                  │   (Offline)     │
        │                  └───────┬─────────┘
        │                          │
        └───────────┬──────────────┘
                    │
        ┌───────────▼──────────────┐
        │    Flask REST API        │
        │   (Python/HTTP)          │
        └───────────┬──────────────┘
                    │
        ┌───────────▼──────────────┐
        │     MongoDB              │
        │  (Cloud Database)        │
        └──────────────────────────┘
```

## Components

### 1. Flask Web Application

**Location**: Root directory
**Technology**: Python 3.11+, Flask 3.1.1, MongoDB
**Purpose**: Web-based storage tracking interface

**Key Features**:
- Google OAuth 2.0 authentication
- CRUD operations for locations and items
- Multi-user data isolation
- Bootstrap 5 responsive UI
- Dark/light theme support
- Sample data scripts

**Main Files**:
- `app.py` - Main Flask application (229 lines, 17 routes)
- `templates/` - Jinja2 HTML templates
- `static/` - CSS and JavaScript assets
- `insert_sample_data.py` - Demo data generator
- `reset_mongo_collections.py` - Database reset utility

**Run Command**:
```bash
python app.py
# Access at http://localhost:5000
```

**Docker Command**:
```bash
docker-compose up
# Flask: http://localhost:5000
# Mongo Express: http://localhost:8081
```

### 2. .NET MAUI Mobile App

**Location**: `MobileApp/` directory
**Technology**: .NET 9, MAUI, Blazor Hybrid, SQLite
**Purpose**: Cross-platform mobile app (Android/iOS)

**Key Features**:
- Offline-first architecture with local SQLite storage
- Bidirectional sync with Flask API
- Google OAuth (with demo mode for testing)
- Native mobile UI using Blazor components
- Full CRUD for locations and items
- Sync status tracking

**Project Structure**:
```
MobileApp/
├── Components/Pages/      # Blazor UI pages
├── Models/                # Data models
├── Data/                  # SQLite service
├── Services/              # API, Auth, Sync
├── Platforms/             # Platform-specific
└── appsettings.json       # Configuration
```

**Build Commands**:
```bash
cd MobileApp

# Android
dotnet build -f net9.0-android
dotnet build -t:Run -f net9.0-android

# iOS (Mac only)
dotnet build -f net9.0-ios
```

### 3. Database Schema

**MongoDB Collections**:

**users**
```javascript
{
  _id: String,           // Google sub or email
  email: String,
  name: String
}
```

**locations**
```javascript
{
  _id: ObjectId,
  name: String,
  description: String,
  user_id: String
}
```
Index: `user_id`

**storage_items**
```javascript
{
  _id: ObjectId,
  name: String,
  brand: String,
  size: String,
  nutritional_info: String,
  date_purchased: String,
  expiration_date: String,
  ingredients: String,
  other_info: String,
  location_id: String,
  user_id: String
}
```
Indexes: `user_id`, `location_id`

**SQLite Tables** (Mobile App):
- Similar schema with additional fields:
  - `IsSynced` - Sync status flag
  - `LastModified` - Timestamp
  - `IsDeleted` - Soft delete flag
  - `ApiId` - MongoDB ID mapping

## API Endpoints

### Authentication
- `GET /` - Home page
- `GET /login` - Initiate OAuth
- `GET /login/authorized` - OAuth callback
- `GET /logout` - Logout

### Locations
- `GET /locations` - List locations
- `POST /locations/add` - Create location
- `GET /locations/<id>` - View location
- `POST /locations/<id>/edit` - Update location
- `POST /locations/<id>/delete` - Delete location

### Items
- `GET /items` - List items
- `POST /items/add` - Create item
- `GET /items/<id>` - View item
- `POST /items/<id>/edit` - Update item
- `POST /items/<id>/delete` - Delete item

## Data Synchronization

The mobile app implements a sophisticated sync mechanism:

### Upload Strategy
1. Detect unsynced local changes (`IsSynced = false`)
2. Upload new records to API
3. Update existing records on API
4. Delete marked records from API
5. Map API IDs to local records
6. Mark records as synced

### Download Strategy
1. Fetch all data from API
2. Create local copies if not exist
3. Preserve local unsynced changes
4. Map API IDs to local IDs
5. Update last sync timestamp

### Conflict Resolution
- Local changes take precedence
- Unsynced items are not overwritten
- Sync is manual (user-initiated)
- Clear visual indication of sync status

## Setup & Installation

### Prerequisites
- Python 3.11+ (for Flask app)
- .NET 9 SDK (for mobile app)
- MongoDB (local or Atlas)
- Docker Desktop (optional, for containerization)
- Visual Studio 2022 (recommended for MAUI)

### Flask App Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
# Copy and edit .env file
SECRET_KEY=your_secret_key
MONGO_URI=mongodb://user:pass@localhost:27017/home_storage
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
USE_AUTH=True
```

3. **Run Application**
```bash
python app.py
```

### Mobile App Setup

1. **Navigate to Mobile App**
```bash
cd MobileApp
```

2. **Restore Packages**
```bash
dotnet restore
```

3. **Build**
```bash
dotnet build -f net9.0-android
```

4. **Run on Emulator**
```bash
dotnet build -t:Run -f net9.0-android
```

### Docker Setup

1. **Start All Services**
```bash
docker-compose up
```

This starts:
- MongoDB on port 27017
- Flask app on port 5000
- Mongo Express on port 8081

## Configuration

### API Base URL (Mobile App)

For **Android Emulator**:
```
http://10.0.2.2:5000
```

For **iOS Simulator**:
```
http://localhost:5000
```

For **Physical Devices**:
```
http://192.168.1.xxx:5000  (your computer's IP)
```

Update in `appsettings.json` or `ApiClient.cs`

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials
3. Add authorized redirect URIs:
   - Web: `http://localhost:5000/login/authorized`
   - Mobile: `com.storagetracker.app:/oauth2redirect`
4. Copy Client ID and Secret to `.env` files

## Testing the Full Stack

### End-to-End Test

1. **Start Flask App**
   ```bash
   python app.py
   ```

2. **Open Web Browser**
   - Navigate to http://localhost:5000
   - Login with Google
   - Create a location (e.g., "Pantry")
   - Add an item to that location

3. **Start Mobile App**
   ```bash
   cd MobileApp
   dotnet build -t:Run -f net9.0-android
   ```

4. **In Mobile App**
   - Use "Demo Login"
   - Click "Sync Now"
   - Verify the location and item appear
   - Create a new item
   - Click "Sync Now" again

5. **Back in Web Browser**
   - Refresh the items page
   - Verify the new item from mobile appears

## File Structure

```
storage-python/
├── app.py                          # Flask application
├── requirements.txt                # Python dependencies
├── docker-compose.yml              # Docker orchestration
├── Dockerfile                      # Flask container
├── entrypoint.sh                   # Docker startup
├── insert_sample_data.py           # Demo data
├── reset_mongo_collections.py     # DB reset
├── .env                            # Local config
├── .env.docker                     # Docker config
├── .gitignore                      # Git ignore rules
├── CODE_OVERVIEW.md                # Flask docs
├── MOBILE_APP_SETUP.md             # Quick start
├── PROJECT_SUMMARY.md              # This file
│
├── static/
│   ├── styles.css                  # Dark mode styles
│   └── theme.js                    # Theme toggle
│
├── templates/
│   ├── base.html                   # Base template
│   ├── index.html                  # Home page
│   ├── locations.html              # Locations list
│   ├── location_form.html          # Location form
│   ├── location_view.html          # Location detail
│   ├── items.html                  # Items list
│   ├── item_form.html              # Item form
│   └── item_view.html              # Item detail
│
└── MobileApp/
    ├── Components/
    │   ├── Pages/
    │   │   ├── Home.razor          # Dashboard
    │   │   ├── Login.razor         # Auth
    │   │   ├── Locations.razor     # List
    │   │   ├── LocationForm.razor  # Form
    │   │   ├── Items.razor         # List
    │   │   └── ItemForm.razor      # Form
    │   └── Layout/
    │       ├── MainLayout.razor    # Layout
    │       └── NavMenu.razor       # Navigation
    ├── Models/
    │   ├── User.cs
    │   ├── Location.cs
    │   └── StorageItem.cs
    ├── Data/
    │   └── DatabaseService.cs      # SQLite ops
    ├── Services/
    │   ├── ApiClient.cs            # HTTP client
    │   ├── AuthService.cs          # Auth
    │   └── SyncService.cs          # Sync logic
    ├── Platforms/                  # Platform code
    ├── MauiProgram.cs              # App config
    ├── appsettings.json            # Config
    └── README.md                   # MAUI docs
```

## Documentation

- **CODE_OVERVIEW.md** - Detailed Flask application documentation
- **MOBILE_APP_SETUP.md** - Quick start for mobile app
- **MobileApp/README.md** - Complete mobile app documentation
- **PROJECT_SUMMARY.md** - This file (overall summary)

## Security Considerations

### Current Implementation
- OAuth tokens in local storage
- Session-based authentication
- User data isolation by `user_id`
- Basic input validation

### Production Recommendations
1. **Enable HTTPS**: Use SSL certificates
2. **Encrypt Local DB**: Use SQLCipher for mobile
3. **Secure Token Storage**: Use SecureStorage API
4. **Add CSRF Protection**: Implement CSRF tokens
5. **Rate Limiting**: Add API rate limits
6. **Input Sanitization**: Validate all inputs
7. **Secret Management**: Use environment variables

## Development Workflow

### Adding New Features

1. **Update Models** (if needed)
   - Flask: Add fields to collections
   - Mobile: Update model classes

2. **Update Database Layer**
   - Flask: Update queries in `app.py`
   - Mobile: Update `DatabaseService.cs`

3. **Update API**
   - Add endpoints in Flask `app.py`
   - Update `ApiClient.cs` in mobile

4. **Update Sync Logic**
   - Modify `SyncService.cs`

5. **Update UI**
   - Flask: Edit Jinja2 templates
   - Mobile: Edit Razor components

6. **Test**
   - Test web interface
   - Test mobile interface
   - Test synchronization

## Deployment

### Flask App Deployment

**Options**:
- Heroku
- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service
- DigitalOcean App Platform

**Requirements**:
- MongoDB Atlas (cloud database)
- Environment variables configured
- HTTPS enabled
- CORS configured for mobile app

### Mobile App Deployment

**Android**:
1. Build release APK
   ```bash
   dotnet build -c Release -f net9.0-android
   ```
2. Sign with keystore
3. Upload to Google Play Store

**iOS**:
1. Build release IPA
   ```bash
   dotnet build -c Release -f net9.0-ios
   ```
2. Archive and sign
3. Upload to App Store Connect

## Performance Optimization

### Flask App
- Use MongoDB indexes (already configured)
- Enable caching for static assets
- Use pagination for large lists
- Optimize database queries
- Use CDN for Bootstrap/JS libraries

### Mobile App
- Lazy load data
- Batch database operations
- Compress images before upload
- Use connection pooling
- Implement pull-to-refresh
- Cache frequently accessed data

## Troubleshooting

### Common Issues

**MongoDB Connection Failed**
- Check MongoDB is running
- Verify connection string in `.env`
- Check firewall rules

**Mobile App Can't Connect to API**
- Use `10.0.2.2:5000` for Android emulator
- Use local IP for physical devices
- Ensure same network (WiFi)
- Check firewall settings

**Build Errors (Mobile)**
```bash
dotnet clean
dotnet restore
dotnet build
```

**Authentication Errors**
- Verify Google OAuth credentials
- Check redirect URIs
- Use demo mode for testing

## Future Enhancements

### Planned Features
- [ ] Push notifications for expiring items
- [ ] Barcode scanning
- [ ] Image attachments
- [ ] Shopping list generation
- [ ] Batch operations
- [ ] Advanced search and filters
- [ ] Export to CSV/PDF
- [ ] Recurring items
- [ ] Share lists with family
- [ ] Auto-sync on app resume

### Technical Improvements
- [ ] Unit tests for both apps
- [ ] Integration tests
- [ ] CI/CD pipeline
- [ ] API versioning
- [ ] GraphQL API option
- [ ] WebSocket for real-time sync
- [ ] Progressive Web App (PWA)
- [ ] Accessibility improvements

## Contributing

### Code Style

**Python (Flask)**:
- Follow PEP 8
- Use type hints where appropriate
- Document functions with docstrings

**C# (.NET)**:
- Follow Microsoft naming conventions
- Use async/await consistently
- Add XML documentation

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Update documentation
5. Submit pull request

## Testing Checklist

- [ ] Create location in web app
- [ ] Create item in web app
- [ ] Edit location in web app
- [ ] Edit item in web app
- [ ] Delete location in web app
- [ ] Delete item in web app
- [ ] Login to mobile app
- [ ] Sync data to mobile
- [ ] Verify data in mobile
- [ ] Create location in mobile
- [ ] Create item in mobile
- [ ] Edit location in mobile
- [ ] Edit item in mobile
- [ ] Sync data to server
- [ ] Verify data in web app
- [ ] Test offline mode
- [ ] Test sync conflict resolution
- [ ] Test theme toggle
- [ ] Test on Android
- [ ] Test on iOS

## Version History

**Version 1.0** (Current)
- Initial release
- Flask web application
- .NET MAUI mobile app
- MongoDB integration
- Google OAuth authentication
- Offline-first sync
- Docker support

## License

[Specify your license here]

## Support

For issues and questions:
- Check documentation files
- Review troubleshooting section
- Check GitHub issues

## Acknowledgments

- Flask Framework
- .NET MAUI Team
- MongoDB
- Google OAuth
- Bootstrap

---

**Project Created**: October 2025
**Last Updated**: 2025-10-28
**Maintained By**: [Your Name]
