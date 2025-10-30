using SQLite;

namespace StorageTrackerMaui.Models
{
    public class Location
    {
        [PrimaryKey]
        public string Id { get; set; } = Guid.NewGuid().ToString();

        public string Name { get; set; } = string.Empty;

        public string Description { get; set; } = string.Empty;

        public string UserId { get; set; } = string.Empty;

        // For tracking sync status
        public bool IsSynced { get; set; }

        public DateTime? LastModified { get; set; }

        public bool IsDeleted { get; set; }

        // API ID from MongoDB (if synced)
        public string? ApiId { get; set; }
    }
}
