using StorageTrackerMaui.Data;
using StorageTrackerMaui.Models;

namespace StorageTrackerMaui.Services
{
    public class AuthService
    {
        private readonly DatabaseService _database;
        private readonly ApiClient _apiClient;

        public AuthService(DatabaseService database, ApiClient apiClient)
        {
            _database = database;
            _apiClient = apiClient;
        }

        // For now, we'll implement a simple authentication mechanism
        // In production, you would integrate with Google Sign-In using MAUI's WebAuthenticator
        public async Task<AuthResult> LoginWithGoogleAsync()
        {
            try
            {
                // MAUI WebAuthenticator for Google Sign-In
                // Note: Requires platform-specific setup for Android and iOS
                var authResult = await WebAuthenticator.Default.AuthenticateAsync(
                    new Uri("https://accounts.google.com/o/oauth2/v2/auth"),
                    new Uri("com.storagetracker.app:/oauth2redirect"));

                if (authResult != null)
                {
                    // Extract user info from the auth result
                    authResult.Properties.TryGetValue("id_token", out var idToken);
                    authResult.Properties.TryGetValue("access_token", out var accessToken);

                    // Decode the ID token to get user info (simplified)
                    // In production, use a proper JWT library
                    var userInfo = ParseGoogleIdToken(idToken ?? "");

                    var user = new User
                    {
                        Id = userInfo.Id,
                        Email = userInfo.Email,
                        Name = userInfo.Name,
                        AccessToken = accessToken,
                        TokenExpiry = DateTime.UtcNow.AddHours(1),
                        IsLoggedIn = true
                    };

                    await _database.SaveUserAsync(user);
                    _apiClient.SetAuthToken(accessToken ?? "");

                    return new AuthResult
                    {
                        Success = true,
                        User = user
                    };
                }
                else
                {
                    return new AuthResult
                    {
                        Success = false,
                        ErrorMessage = "Authentication cancelled"
                    };
                }
            }
            catch (TaskCanceledException)
            {
                return new AuthResult
                {
                    Success = false,
                    ErrorMessage = "Authentication cancelled by user"
                };
            }
            catch (Exception ex)
            {
                return new AuthResult
                {
                    Success = false,
                    ErrorMessage = $"Authentication failed: {ex.Message}"
                };
            }
        }

        // Demo login for testing without OAuth
        public async Task<AuthResult> DemoLoginAsync(string email, string name)
        {
            var user = new User
            {
                Id = email,
                Email = email,
                Name = name,
                AccessToken = "demo_token",
                TokenExpiry = DateTime.UtcNow.AddDays(30),
                IsLoggedIn = true
            };

            await _database.SaveUserAsync(user);

            return new AuthResult
            {
                Success = true,
                User = user
            };
        }

        public async Task<bool> IsAuthenticatedAsync()
        {
            var user = await _database.GetCurrentUserAsync();
            return user != null && user.IsLoggedIn;
        }

        public async Task<User?> GetCurrentUserAsync()
        {
            return await _database.GetCurrentUserAsync();
        }

        public async Task LogoutAsync()
        {
            await _database.LogoutAsync();
        }

        private UserInfo ParseGoogleIdToken(string idToken)
        {
            // Simplified token parsing
            // In production, use a proper JWT library like System.IdentityModel.Tokens.Jwt
            try
            {
                var parts = idToken.Split('.');
                if (parts.Length >= 2)
                {
                    var payload = parts[1];
                    // Decode base64url
                    var jsonPayload = System.Text.Encoding.UTF8.GetString(
                        Convert.FromBase64String(payload.PadRight(payload.Length + (4 - payload.Length % 4) % 4, '=')));

                    // Parse JSON (simplified)
                    // You would use Newtonsoft.Json or System.Text.Json here
                    return new UserInfo
                    {
                        Id = "demo_user_id",
                        Email = "user@example.com",
                        Name = "Demo User"
                    };
                }
            }
            catch { }

            return new UserInfo
            {
                Id = Guid.NewGuid().ToString(),
                Email = "demo@example.com",
                Name = "Demo User"
            };
        }
    }

    public class AuthResult
    {
        public bool Success { get; set; }
        public User? User { get; set; }
        public string ErrorMessage { get; set; } = string.Empty;
    }

    public class UserInfo
    {
        public string Id { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
    }
}
