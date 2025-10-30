# Mobile App Quick Start Guide

This document provides quick instructions for getting started with the Storage Tracker mobile app.

## What's Included

A complete .NET MAUI Blazor Hybrid mobile application has been created in the `MobileApp/` folder with:

- Cross-platform support (Android & iOS)
- Local SQLite database for offline storage
- Synchronization with the Flask API backend
- Google OAuth authentication (with demo mode)
- Blazor-based responsive UI

## Quick Start (Demo Mode)

The easiest way to test the mobile app is using demo mode:

### Step 1: Ensure Flask API is Running

```bash
# From the storage-python directory
python app.py
```

The Flask API should be running at http://localhost:5000

### Step 2: Configure API URL

For Android Emulator, the app is configured to use `http://10.0.2.2:5000` (which maps to localhost on your computer).

For iOS Simulator or physical devices, you'll need to update the API URL to your computer's local IP address.

### Step 3: Build and Run

**Using Visual Studio 2022:**
1. Open `StorageTrackerMaui.csproj` in Visual Studio
2. Select your target (Android Emulator or iOS Simulator)
3. Press F5 to build and run

**Using Command Line:**
```bash
cd MobileApp

# For Android
dotnet build -t:Run -f net9.0-android

# For iOS (Mac only)
dotnet build -t:Run -f net9.0-ios
```

### Step 4: Login

1. App will open to the home page and redirect to login
2. Click "Demo Login" (no setup required)
3. Enter a name and email (any values work)
4. Click "Demo Login" button

### Step 5: Use the App

1. **Create Locations**: Navigate to "Locations" → Click "Add Location"
2. **Add Items**: Navigate to "Items" → Click "Add Item"
3. **Sync**: Go to Home → Click "Sync Now" to sync with the Flask backend

## Features Overview

### Offline-First Architecture
- All data stored locally in SQLite
- Works completely offline
- Sync when connection available

### Synchronization
- Bidirectional sync with Flask API
- Tracks sync status for each record
- Unsynced changes clearly marked
- Manual sync via "Sync Now" button

### Data Management
- **Locations**: Manage storage locations (pantry, garage, etc.)
- **Items**: Track individual items with details:
  - Name, brand, size
  - Purchase and expiration dates
  - Nutritional info and ingredients
  - Location assignment

### Authentication
- **Demo Mode**: Quick login for testing (no configuration)
- **Google OAuth**: Production-ready authentication (requires setup)

## API Integration

The mobile app connects to the Flask API at these endpoints:

- `GET /locations` - Fetch locations
- `POST /locations/add` - Create location
- `POST /locations/{id}/edit` - Update location
- `POST /locations/{id}/delete` - Delete location
- `GET /items` - Fetch items
- `POST /items/add` - Create item
- `POST /items/{id}/edit` - Update item
- `POST /items/{id}/delete` - Delete item

## Project Structure

```
MobileApp/
├── Components/Pages/        # Blazor pages (UI)
├── Models/                  # Data models
├── Data/                    # SQLite database service
├── Services/                # API client, Auth, Sync
├── Platforms/               # Platform-specific code
└── appsettings.json        # Configuration
```

## Key Files

- **MauiProgram.cs**: Service registration and configuration
- **DatabaseService.cs**: Local SQLite operations
- **ApiClient.cs**: HTTP client for Flask API
- **SyncService.cs**: Bidirectional sync logic
- **AuthService.cs**: Authentication handling

## Testing the Sync

1. **Create data in mobile app** while offline
2. **Sync** using "Sync Now" button
3. **Verify in web app** - Open http://localhost:5000 in browser
4. **Create data in web app**
5. **Sync in mobile app** again
6. **Verify** data appears in mobile app

## Troubleshooting

### Can't Connect to API

**Android Emulator:**
- Use `http://10.0.2.2:5000` (not localhost)
- This is pre-configured in the app

**iOS Simulator:**
- Use `http://localhost:5000`
- Or your Mac's IP address

**Physical Device:**
- Use your computer's local network IP
- Example: `http://192.168.1.100:5000`
- Ensure device is on same WiFi network
- Check firewall settings

### Build Errors

```bash
# Clean and restore
dotnet clean
dotnet restore
dotnet build
```

### Database Issues

Clear app data:
- Android: Settings → Apps → Storage Tracker → Clear Data
- iOS: Uninstall and reinstall app

## Development Tips

### Viewing the SQLite Database

**Android:**
1. Use Android Device File Explorer in Visual Studio
2. Navigate to: `/data/data/com.companyname.storagetrackermui/files/`
3. Download `storage_tracker.db3`
4. Open with DB Browser for SQLite

**iOS:**
1. Access via Xcode device browser
2. Location: `Application Support/storage_tracker.db3`

### Debugging

Add breakpoints in:
- `DatabaseService.cs` - Database operations
- `ApiClient.cs` - API calls
- `SyncService.cs` - Sync logic

Use debug output:
```csharp
Console.WriteLine($"Debug: {message}");
```

## Google OAuth Setup (Advanced)

To enable production Google Sign-In:

### 1. Google Cloud Console Setup
1. Go to https://console.cloud.google.com
2. Create new project or select existing
3. Enable Google Sign-In API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs

### 2. Android Configuration
1. Add package name: `com.companyname.storagetrackermui`
2. Add SHA-1 certificate fingerprint
3. Configure intent filter in AndroidManifest.xml

### 3. iOS Configuration
1. Add URL scheme to Info.plist
2. Configure CFBundleURLTypes
3. Handle auth callback

## Next Steps

1. **Read Full Documentation**: See `MobileApp/README.md`
2. **Test Sync Functionality**: Create data and sync
3. **Customize UI**: Modify Blazor pages
4. **Add Features**: Extend functionality
5. **Deploy**: Build release versions for app stores

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│         Mobile App (MAUI)               │
│  ┌────────────────────────────────┐    │
│  │   Blazor UI Components         │    │
│  └──────────┬─────────────────────┘    │
│             │                           │
│  ┌──────────▼─────────────────────┐    │
│  │   Services Layer               │    │
│  │  - AuthService                 │    │
│  │  - SyncService                 │    │
│  │  - ApiClient                   │    │
│  └──────┬─────────────┬───────────┘    │
│         │             │                 │
│  ┌──────▼───────┐  ┌─▼──────────┐     │
│  │   SQLite DB  │  │  Flask API │     │
│  │   (Local)    │  │  (Cloud)   │     │
│  └──────────────┘  └────────────┘     │
└─────────────────────────────────────────┘
```

## Support

For detailed documentation, see:
- `MobileApp/README.md` - Complete mobile app documentation
- `CODE_OVERVIEW.md` - Flask API documentation

## Summary

The mobile app provides a complete offline-first solution that:
- Works without internet connection
- Syncs data with Flask backend when online
- Provides native mobile experience
- Shares authentication with web app
- Uses responsive Blazor UI

Start with demo mode to test quickly, then configure Google OAuth for production use.
