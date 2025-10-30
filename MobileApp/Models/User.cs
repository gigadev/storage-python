using SQLite;

namespace StorageTrackerMaui.Models
{
    public class User
    {
        [PrimaryKey]
        public string Id { get; set; } = string.Empty;

        public string Email { get; set; } = string.Empty;

        public string Name { get; set; } = string.Empty;

        public string? AccessToken { get; set; }

        public DateTime? TokenExpiry { get; set; }

        public bool IsLoggedIn { get; set; }

        public DateTime? LastSyncDate { get; set; }
    }
}
