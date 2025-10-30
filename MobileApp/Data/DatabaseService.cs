using SQLite;
using StorageTrackerMaui.Models;
using Location = StorageTrackerMaui.Models.Location;

namespace StorageTrackerMaui.Data
{
    public class DatabaseService
    {
        private SQLiteAsyncConnection? _database;

        public async Task InitializeAsync()
        {
            if (_database != null)
                return;

            var dbPath = Path.Combine(FileSystem.AppDataDirectory, "storage_tracker.db3");
            _database = new SQLiteAsyncConnection(dbPath);

            await _database.CreateTableAsync<User>();
            await _database.CreateTableAsync<Location>();
            await _database.CreateTableAsync<StorageItem>();
        }

        private async Task<SQLiteAsyncConnection> GetDatabaseAsync()
        {
            if (_database == null)
                await InitializeAsync();
            return _database!;
        }

        // User operations
        public async Task<User?> GetCurrentUserAsync()
        {
            var db = await GetDatabaseAsync();
            return await db.Table<User>()
                .Where(u => u.IsLoggedIn)
                .FirstOrDefaultAsync();
        }

        public async Task<int> SaveUserAsync(User user)
        {
            var db = await GetDatabaseAsync();
            var existing = await db.Table<User>()
                .Where(u => u.Id == user.Id)
                .FirstOrDefaultAsync();

            if (existing != null)
                return await db.UpdateAsync(user);
            else
                return await db.InsertAsync(user);
        }

        public async Task LogoutAsync()
        {
            var db = await GetDatabaseAsync();
            var users = await db.Table<User>().ToListAsync();
            foreach (var user in users)
            {
                user.IsLoggedIn = false;
                await db.UpdateAsync(user);
            }
        }

        // Location operations
        public async Task<List<Location>> GetLocationsAsync(string userId)
        {
            var db = await GetDatabaseAsync();
            return await db.Table<Location>()
                .Where(l => l.UserId == userId && !l.IsDeleted)
                .OrderBy(l => l.Name)
                .ToListAsync();
        }

        public async Task<Location?> GetLocationAsync(string id)
        {
            var db = await GetDatabaseAsync();
            return await db.Table<Location>()
                .Where(l => l.Id == id)
                .FirstOrDefaultAsync();
        }

        public async Task<int> SaveLocationAsync(Location location)
        {
            var db = await GetDatabaseAsync();
            location.LastModified = DateTime.UtcNow;
            location.IsSynced = false;

            var existing = await db.Table<Location>()
                .Where(l => l.Id == location.Id)
                .FirstOrDefaultAsync();

            if (existing != null)
                return await db.UpdateAsync(location);
            else
                return await db.InsertAsync(location);
        }

        public async Task<int> DeleteLocationAsync(string id)
        {
            var db = await GetDatabaseAsync();
            var location = await GetLocationAsync(id);
            if (location != null)
            {
                location.IsDeleted = true;
                location.IsSynced = false;
                location.LastModified = DateTime.UtcNow;
                return await db.UpdateAsync(location);
            }
            return 0;
        }

        // Storage Item operations
        public async Task<List<StorageItem>> GetStorageItemsAsync(string userId)
        {
            var db = await GetDatabaseAsync();
            var items = await db.Table<StorageItem>()
                .Where(i => i.UserId == userId && !i.IsDeleted)
                .OrderBy(i => i.Name)
                .ToListAsync();

            // Load location names
            foreach (var item in items)
            {
                var location = await GetLocationAsync(item.LocationId);
                item.LocationName = location?.Name;
            }

            return items;
        }

        public async Task<List<StorageItem>> GetStorageItemsByLocationAsync(string locationId)
        {
            var db = await GetDatabaseAsync();
            return await db.Table<StorageItem>()
                .Where(i => i.LocationId == locationId && !i.IsDeleted)
                .OrderBy(i => i.Name)
                .ToListAsync();
        }

        public async Task<StorageItem?> GetStorageItemAsync(string id)
        {
            var db = await GetDatabaseAsync();
            var item = await db.Table<StorageItem>()
                .Where(i => i.Id == id)
                .FirstOrDefaultAsync();

            if (item != null)
            {
                var location = await GetLocationAsync(item.LocationId);
                item.LocationName = location?.Name;
            }

            return item;
        }

        public async Task<int> SaveStorageItemAsync(StorageItem item)
        {
            var db = await GetDatabaseAsync();
            item.LastModified = DateTime.UtcNow;
            item.IsSynced = false;

            var existing = await db.Table<StorageItem>()
                .Where(i => i.Id == item.Id)
                .FirstOrDefaultAsync();

            if (existing != null)
                return await db.UpdateAsync(item);
            else
                return await db.InsertAsync(item);
        }

        public async Task<int> DeleteStorageItemAsync(string id)
        {
            var db = await GetDatabaseAsync();
            var item = await GetStorageItemAsync(id);
            if (item != null)
            {
                item.IsDeleted = true;
                item.IsSynced = false;
                item.LastModified = DateTime.UtcNow;
                return await db.UpdateAsync(item);
            }
            return 0;
        }

        // Sync operations
        public async Task<List<Location>> GetUnsyncedLocationsAsync(string userId)
        {
            var db = await GetDatabaseAsync();
            return await db.Table<Location>()
                .Where(l => l.UserId == userId && !l.IsSynced)
                .ToListAsync();
        }

        public async Task<List<StorageItem>> GetUnsyncedItemsAsync(string userId)
        {
            var db = await GetDatabaseAsync();
            return await db.Table<StorageItem>()
                .Where(i => i.UserId == userId && !i.IsSynced)
                .ToListAsync();
        }

        public async Task MarkLocationSyncedAsync(string id, string? apiId = null)
        {
            var db = await GetDatabaseAsync();
            var location = await GetLocationAsync(id);
            if (location != null)
            {
                location.IsSynced = true;
                if (!string.IsNullOrEmpty(apiId))
                    location.ApiId = apiId;
                await db.UpdateAsync(location);
            }
        }

        public async Task MarkItemSyncedAsync(string id, string? apiId = null)
        {
            var db = await GetDatabaseAsync();
            var item = await GetStorageItemAsync(id);
            if (item != null)
            {
                item.IsSynced = true;
                if (!string.IsNullOrEmpty(apiId))
                    item.ApiId = apiId;
                await db.UpdateAsync(item);
            }
        }

        public async Task UpdateLastSyncAsync(string userId)
        {
            var db = await GetDatabaseAsync();
            var user = await db.Table<User>()
                .Where(u => u.Id == userId)
                .FirstOrDefaultAsync();

            if (user != null)
            {
                user.LastSyncDate = DateTime.UtcNow;
                await db.UpdateAsync(user);
            }
        }
    }
}
