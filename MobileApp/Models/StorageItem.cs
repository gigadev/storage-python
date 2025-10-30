using SQLite;

namespace StorageTrackerMaui.Models
{
    public class StorageItem
    {
        [PrimaryKey]
        public string Id { get; set; } = Guid.NewGuid().ToString();

        public string Name { get; set; } = string.Empty;

        public string Brand { get; set; } = string.Empty;

        public string Size { get; set; } = string.Empty;

        public string NutritionalInfo { get; set; } = string.Empty;

        public string DatePurchased { get; set; } = string.Empty;

        public string ExpirationDate { get; set; } = string.Empty;

        public string Ingredients { get; set; } = string.Empty;

        public string OtherInfo { get; set; } = string.Empty;

        public string LocationId { get; set; } = string.Empty;

        public string UserId { get; set; } = string.Empty;

        // For tracking sync status
        public bool IsSynced { get; set; }

        public DateTime? LastModified { get; set; }

        public bool IsDeleted { get; set; }

        // API ID from MongoDB (if synced)
        public string? ApiId { get; set; }

        // Navigation property (not stored in DB)
        [Ignore]
        public string? LocationName { get; set; }
    }
}
