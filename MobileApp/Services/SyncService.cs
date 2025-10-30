using StorageTrackerMaui.Data;
using StorageTrackerMaui.Models;
using Location = StorageTrackerMaui.Models.Location;

namespace StorageTrackerMaui.Services
{
    public class SyncService
    {
        private readonly DatabaseService _database;
        private readonly ApiClient _apiClient;

        public SyncService(DatabaseService database, ApiClient apiClient)
        {
            _database = database;
            _apiClient = apiClient;
        }

        public async Task<SyncResult> SyncAllAsync()
        {
            var result = new SyncResult();

            try
            {
                var user = await _database.GetCurrentUserAsync();
                if (user == null || string.IsNullOrEmpty(user.AccessToken))
                {
                    result.Success = false;
                    result.Message = "User not authenticated";
                    return result;
                }

                // Test connectivity
                if (!await _apiClient.TestConnectionAsync())
                {
                    result.Success = false;
                    result.Message = "Cannot connect to server";
                    return result;
                }

                // Sync locations first
                await SyncLocationsAsync(user.Id, result);

                // Then sync items
                await SyncItemsAsync(user.Id, result);

                // Update last sync date
                await _database.UpdateLastSyncAsync(user.Id);

                result.Success = true;
                result.Message = $"Sync completed: {result.LocationsUploaded + result.ItemsUploaded} uploaded, {result.LocationsDownloaded + result.ItemsDownloaded} downloaded";
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.Message = $"Sync failed: {ex.Message}";
            }

            return result;
        }

        private async Task SyncLocationsAsync(string userId, SyncResult result)
        {
            // Download locations from API
            var apiLocations = await _apiClient.GetLocationsAsync();
            result.LocationsDownloaded = apiLocations.Count;

            foreach (var apiLocation in apiLocations)
            {
                var existingLocation = await _database.GetLocationsAsync(userId);
                var local = existingLocation.FirstOrDefault(l => l.ApiId == apiLocation.Id);

                if (local == null)
                {
                    // Create new local location
                    var newLocation = new Location
                    {
                        Id = Guid.NewGuid().ToString(),
                        ApiId = apiLocation.Id,
                        Name = apiLocation.Name,
                        Description = apiLocation.Description,
                        UserId = userId,
                        IsSynced = true,
                        LastModified = DateTime.UtcNow
                    };
                    await _database.SaveLocationAsync(newLocation);
                    await _database.MarkLocationSyncedAsync(newLocation.Id, apiLocation.Id);
                }
                else if (!local.IsSynced)
                {
                    // Local changes exist, keep local version but mark as synced
                    await _database.MarkLocationSyncedAsync(local.Id, apiLocation.Id);
                }
            }

            // Upload unsynced local locations
            var unsyncedLocations = await _database.GetUnsyncedLocationsAsync(userId);
            result.LocationsUploaded = unsyncedLocations.Count;

            foreach (var location in unsyncedLocations)
            {
                if (location.IsDeleted && !string.IsNullOrEmpty(location.ApiId))
                {
                    // Delete from API
                    await _apiClient.DeleteLocationAsync(location.ApiId);
                    await _database.MarkLocationSyncedAsync(location.Id);
                }
                else if (!location.IsDeleted)
                {
                    if (string.IsNullOrEmpty(location.ApiId))
                    {
                        // Create new on API
                        var created = await _apiClient.CreateLocationAsync(location);
                        if (created != null)
                        {
                            await _database.MarkLocationSyncedAsync(location.Id, created.Id);
                        }
                    }
                    else
                    {
                        // Update existing on API
                        await _apiClient.UpdateLocationAsync(location.ApiId, location);
                        await _database.MarkLocationSyncedAsync(location.Id);
                    }
                }
            }
        }

        private async Task SyncItemsAsync(string userId, SyncResult result)
        {
            // Download items from API
            var apiItems = await _apiClient.GetStorageItemsAsync();
            result.ItemsDownloaded = apiItems.Count;

            foreach (var apiItem in apiItems)
            {
                var existingItems = await _database.GetStorageItemsAsync(userId);
                var local = existingItems.FirstOrDefault(i => i.ApiId == apiItem.Id);

                if (local == null)
                {
                    // Find local location by API ID
                    var locations = await _database.GetLocationsAsync(userId);
                    var location = locations.FirstOrDefault(l => l.ApiId == apiItem.LocationId);

                    if (location != null)
                    {
                        // Create new local item
                        var newItem = new StorageItem
                        {
                            Id = Guid.NewGuid().ToString(),
                            ApiId = apiItem.Id,
                            Name = apiItem.Name,
                            Brand = apiItem.Brand,
                            Size = apiItem.Size,
                            NutritionalInfo = apiItem.NutritionalInfo,
                            DatePurchased = apiItem.DatePurchased,
                            ExpirationDate = apiItem.ExpirationDate,
                            Ingredients = apiItem.Ingredients,
                            OtherInfo = apiItem.OtherInfo,
                            LocationId = location.Id,
                            UserId = userId,
                            IsSynced = true,
                            LastModified = DateTime.UtcNow
                        };
                        await _database.SaveStorageItemAsync(newItem);
                        await _database.MarkItemSyncedAsync(newItem.Id, apiItem.Id);
                    }
                }
                else if (!local.IsSynced)
                {
                    // Local changes exist, keep local version but mark as synced
                    await _database.MarkItemSyncedAsync(local.Id, apiItem.Id);
                }
            }

            // Upload unsynced local items
            var unsyncedItems = await _database.GetUnsyncedItemsAsync(userId);
            result.ItemsUploaded = unsyncedItems.Count;

            foreach (var item in unsyncedItems)
            {
                // Get location API ID
                var location = await _database.GetLocationAsync(item.LocationId);
                if (location == null || string.IsNullOrEmpty(location.ApiId))
                    continue;

                if (item.IsDeleted && !string.IsNullOrEmpty(item.ApiId))
                {
                    // Delete from API
                    await _apiClient.DeleteStorageItemAsync(item.ApiId);
                    await _database.MarkItemSyncedAsync(item.Id);
                }
                else if (!item.IsDeleted)
                {
                    if (string.IsNullOrEmpty(item.ApiId))
                    {
                        // Create new on API
                        var created = await _apiClient.CreateStorageItemAsync(item, location.ApiId);
                        if (created != null)
                        {
                            await _database.MarkItemSyncedAsync(item.Id, created.Id);
                        }
                    }
                    else
                    {
                        // Update existing on API
                        await _apiClient.UpdateStorageItemAsync(item.ApiId, item, location.ApiId);
                        await _database.MarkItemSyncedAsync(item.Id);
                    }
                }
            }
        }
    }

    public class SyncResult
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public int LocationsUploaded { get; set; }
        public int LocationsDownloaded { get; set; }
        public int ItemsUploaded { get; set; }
        public int ItemsDownloaded { get; set; }
    }
}
