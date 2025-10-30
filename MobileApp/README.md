# Storage Tracker Mobile App

A .NET MAUI Blazor Hybrid mobile application for tracking home storage inventory with offline-first capabilities and cloud synchronization.

## Overview

This is a cross-platform mobile application (Android & iOS) that syncs with the Flask-based Storage Tracker API. The app provides:

- **Offline-first architecture** with local SQLite storage
- **Cloud synchronization** with the Flask backend API
- **Google OAuth authentication** (with demo mode for testing)
- **Cross-platform support** for Android and iOS
- **Modern Blazor UI** with responsive design

## Technology Stack

- **.NET 9 MAUI** - Cross-platform framework
- **Blazor Hybrid** - Web UI in native apps
- **SQLite** - Local database storage
- **sqlite-net-pcl** - SQLite ORM
- **Newtonsoft.Json** - JSON serialization
- **Bootstrap 5** - UI framework

## Project Structure

```
MobileApp/
├── Components/
│   ├── Pages/
│   │   ├── Home.razor              # Dashboard with sync
│   │   ├── Login.razor             # Authentication page
│   │   ├── Locations.razor         # Location list
│   │   ├── LocationForm.razor      # Add/edit location
│   │   ├── Items.razor             # Item list
│   │   └── ItemForm.razor          # Add/edit item
│   └── Layout/
│       ├── MainLayout.razor        # App layout
│       └── NavMenu.razor           # Navigation menu
├── Models/
│   ├── User.cs                     # User model
│   ├── Location.cs                 # Location model
│   └── StorageItem.cs              # Item model
├── Data/
│   └── DatabaseService.cs          # SQLite operations
├── Services/
│   ├── ApiClient.cs                # Flask API client
│   ├── AuthService.cs              # Authentication
│   └── SyncService.cs              # Sync logic
├── Platforms/                      # Platform-specific code
├── MauiProgram.cs                  # App configuration
└── README.md                       # This file
```

## Features

### 1. Local Storage (SQLite)

All data is stored locally in an SQLite database with the following tables:

- **users** - User authentication and profile
- **locations** - Storage locations
- **storage_items** - Inventory items

Each record tracks:
- Sync status (IsSynced flag)
- Last modification date
- Soft delete status (IsDeleted)
- API ID mapping for synced records

### 2. Cloud Synchronization

The app uses a bidirectional sync strategy:

**Download from API:**
- Fetches all locations and items from the server
- Creates local copies if they don't exist
- Preserves local changes if not synced

**Upload to API:**
- Sends unsynced local changes to the server
- Creates new records on the server
- Updates existing records
- Deletes records marked for deletion

**Sync Process:**
1. Locations are synced first (items depend on locations)
2. Items are synced after locations
3. Local and API IDs are mapped and tracked
4. Last sync timestamp is recorded

### 3. Authentication

**Google OAuth (Production):**
- Uses MAUI's WebAuthenticator
- Redirects to Google Sign-In
- Extracts ID token and access token
- Stores user credentials locally

**Demo Mode (Development):**
- Quick login without OAuth setup
- Useful for testing and development
- Uses mock credentials

### 4. Offline-First Architecture

- All operations work offline by default
- Data is immediately available from local storage
- Sync happens on-demand via "Sync Now" button
- Unsynced items are clearly marked in the UI
- Conflict resolution favors local changes

## Setup Instructions

### Prerequisites

- .NET 9 SDK or later
- Visual Studio 2022 (Windows) or Visual Studio for Mac
- Android SDK (for Android development)
- Xcode (for iOS development, Mac only)

### 1. Install Dependencies

The required NuGet packages are already referenced:

```bash
dotnet restore
```

### 2. Configure API Connection

Update the API base URL in your code or configuration:

```csharp
// In Home.razor.cs or a configuration file
var apiClient = new ApiClient();
apiClient.SetBaseUrl("http://your-api-server:5000");
```

For local development with Android emulator:
- Use `http://10.0.2.2:5000` (Android emulator loopback)

For local development with physical device:
- Use your computer's IP address: `http://192.168.1.x:5000`

### 3. Google OAuth Setup (Optional)

To enable Google Sign-In:

#### Android
1. Register your app in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Add the callback URL: `com.storagetracker.app:/oauth2redirect`
4. Update `AndroidManifest.xml` with the callback intent filter

#### iOS
1. Register your app in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Add the callback URL to `Info.plist`
4. Configure URL schemes

### 4. Build and Run

#### Android
```bash
dotnet build -t:Run -f net9.0-android
```

Or in Visual Studio:
- Set `StorageTrackerMaui` as startup project
- Select Android emulator or device
- Press F5 to debug

#### iOS
```bash
dotnet build -t:Run -f net9.0-ios
```

Or in Visual Studio for Mac:
- Set `StorageTrackerMaui` as startup project
- Select iOS simulator or device
- Press F5 to debug

## Usage

### First Time Setup

1. **Launch the App**
   - App opens to the home screen
   - Redirects to login if not authenticated

2. **Login**
   - Use "Demo Login" for quick testing
   - Or "Login with Google" for production

3. **Create Locations**
   - Navigate to "Locations"
   - Click "Add Location"
   - Enter name and description
   - Save

4. **Add Items**
   - Navigate to "Items"
   - Click "Add Item"
   - Fill in item details
   - Select a location
   - Save

5. **Sync with Cloud**
   - Return to Home screen
   - Click "Sync Now"
   - Wait for sync to complete
   - Check sync status message

### Offline Usage

The app works fully offline:
- Create, edit, and delete locations and items
- All changes are saved locally
- Unsynced items show a "Not Synced" badge
- Sync when connection is available

### Syncing Data

**Manual Sync:**
- Go to Home screen
- Click "Sync Now" button
- View sync results (uploaded/downloaded counts)

**Sync Behavior:**
- First sync downloads all server data
- Subsequent syncs are incremental
- Local changes are uploaded
- Server data is downloaded
- Conflicts favor local changes

## Database Schema

### User Table
```csharp
{
    Id: string (primary key)
    Email: string
    Name: string
    AccessToken: string?
    TokenExpiry: DateTime?
    IsLoggedIn: bool
    LastSyncDate: DateTime?
}
```

### Location Table
```csharp
{
    Id: string (primary key)
    Name: string
    Description: string
    UserId: string
    IsSynced: bool
    LastModified: DateTime?
    IsDeleted: bool
    ApiId: string? (MongoDB _id when synced)
}
```

### StorageItem Table
```csharp
{
    Id: string (primary key)
    Name: string
    Brand: string
    Size: string
    NutritionalInfo: string
    DatePurchased: string
    ExpirationDate: string
    Ingredients: string
    OtherInfo: string
    LocationId: string (foreign key)
    UserId: string
    IsSynced: bool
    LastModified: DateTime?
    IsDeleted: bool
    ApiId: string? (MongoDB _id when synced)
}
```

## API Integration

The app communicates with the Flask API using these endpoints:

### Authentication
- OAuth handled by Google directly
- Token sent in Authorization header

### Locations
- `GET /locations` - List all locations
- `GET /locations/{id}` - Get single location
- `POST /locations/add` - Create location
- `POST /locations/{id}/edit` - Update location
- `POST /locations/{id}/delete` - Delete location

### Items
- `GET /items` - List all items
- `GET /items/{id}` - Get single item
- `POST /items/add` - Create item
- `POST /items/{id}/edit` - Update item
- `POST /items/{id}/delete` - Delete item

## Development

### Adding New Features

1. **Add Model Properties**
   - Update model classes in `Models/`
   - Add SQLite attributes if needed

2. **Update Database Service**
   - Add new CRUD operations in `DatabaseService.cs`
   - Implement queries and updates

3. **Update API Client**
   - Add new API methods in `ApiClient.cs`
   - Map to Flask endpoints

4. **Update Sync Service**
   - Add sync logic for new entities
   - Handle upload/download

5. **Create/Update UI**
   - Add Blazor pages in `Components/Pages/`
   - Update navigation in `NavMenu.razor`

### Debugging

**SQLite Database Location:**
- Android: `/data/data/com.companyname.storagetrackermui/files/storage_tracker.db3`
- iOS: `~/Library/Application Support/storage_tracker.db3`

**View Database:**
Use Android Device Monitor or download the database file to view with SQLite browser.

**Logging:**
Add debug logging in services:
```csharp
Console.WriteLine($"Debug: {message}");
```

## Troubleshooting

### Sync Fails

**Problem:** "Cannot connect to server" error

**Solutions:**
- Check API server is running
- Verify API URL is correct
- For Android emulator, use `10.0.2.2` not `localhost`
- Check firewall settings
- Ensure phone is on same network (for physical devices)

### Authentication Fails

**Problem:** Google OAuth not working

**Solutions:**
- Use Demo Login for testing
- Verify Google OAuth credentials
- Check platform-specific configuration
- Ensure redirect URI is correct

### Database Errors

**Problem:** SQLite exceptions

**Solutions:**
- Check model attributes
- Verify foreign keys exist
- Clear app data and reinstall
- Check database initialization

### Build Errors

**Problem:** Compilation errors

**Solutions:**
- Restore NuGet packages: `dotnet restore`
- Clean solution: `dotnet clean`
- Rebuild: `dotnet build`
- Update .NET SDK if needed

## Performance Considerations

### Optimization Tips

1. **Lazy Loading**
   - Only load data when needed
   - Use pagination for large lists

2. **Batch Operations**
   - Group database operations
   - Use transactions for multiple writes

3. **Caching**
   - Cache frequently accessed data
   - Invalidate cache on updates

4. **Background Sync**
   - Consider auto-sync in background
   - Use MAUI background tasks

5. **Image Handling**
   - Compress images before upload
   - Use thumbnails for lists

## Security Considerations

### Current Implementation

- OAuth tokens stored in local database
- No token refresh implemented
- Local database not encrypted
- HTTP connections supported

### Production Recommendations

1. **Encrypt Local Database**
   ```csharp
   // Use SQLCipher for encryption
   var options = new SQLiteConnectionString(dbPath,
       SQLiteOpenFlags.Create | SQLiteOpenFlags.ReadWrite,
       storeDateTimeAsTicks: true,
       key: "your-encryption-key");
   ```

2. **Secure Token Storage**
   - Use MAUI SecureStorage
   - Implement token refresh
   - Set appropriate expiration

3. **HTTPS Only**
   - Enforce HTTPS for API calls
   - Add certificate pinning

4. **Input Validation**
   - Validate all user input
   - Sanitize before API calls
   - Prevent SQL injection

## Future Enhancements

- [ ] Auto-sync on app resume
- [ ] Background sync service
- [ ] Conflict resolution UI
- [ ] Barcode scanning for products
- [ ] Image attachments
- [ ] Push notifications for expiring items
- [ ] Export to CSV/PDF
- [ ] Search and filter
- [ ] Offline change history
- [ ] Batch operations

## Testing

### Manual Testing Checklist

- [ ] Login with demo credentials
- [ ] Create location offline
- [ ] Create item offline
- [ ] Edit location offline
- [ ] Edit item offline
- [ ] Delete location offline
- [ ] Delete item offline
- [ ] Sync with server
- [ ] Verify data on web app
- [ ] Make changes on web app
- [ ] Sync from server
- [ ] Test with no internet connection
- [ ] Test logout and login

### Unit Testing

Add unit tests for:
- Database operations
- Sync logic
- API client
- Authentication

## Contributing

When contributing to the mobile app:

1. Follow .NET naming conventions
2. Add XML documentation to public APIs
3. Test on both Android and iOS
4. Update this README with new features
5. Ensure offline functionality works
6. Test sync scenarios thoroughly

## License

Same as parent project.

## Support

For issues related to the mobile app:
1. Check this README first
2. Review troubleshooting section
3. Check the main project documentation
4. Report issues with platform details (Android/iOS version)

---

**Last Updated**: 2025-10-28
**Version**: 1.0.0
**.NET Version**: 9.0
**MAUI Version**: Latest
