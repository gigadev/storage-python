using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using StorageTrackerMaui.Models;
using System.Net.Http.Headers;
using System.Text;
using Location = StorageTrackerMaui.Models.Location;

namespace StorageTrackerMaui.Services
{
    public class ApiClient
    {
        private readonly HttpClient _httpClient;
        private string _baseUrl = "http://localhost:5000"; // Default, should be configured

        public ApiClient()
        {
            _httpClient = new HttpClient();
            _httpClient.Timeout = TimeSpan.FromSeconds(30);
        }

        public void SetBaseUrl(string baseUrl)
        {
            _baseUrl = baseUrl.TrimEnd('/');
        }

        public void SetAuthToken(string token)
        {
            _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
        }

        // Helper method to handle API responses
        private async Task<T?> HandleResponseAsync<T>(HttpResponseMessage response)
        {
            if (!response.IsSuccessStatusCode)
            {
                var error = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException($"API Error: {response.StatusCode} - {error}");
            }

            var content = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<T>(content);
        }

        // Location API methods
        public async Task<List<ApiLocation>> GetLocationsAsync()
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/locations");
            var locations = await HandleResponseAsync<List<ApiLocation>>(response);
            return locations ?? new List<ApiLocation>();
        }

        public async Task<ApiLocation?> GetLocationAsync(string id)
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/locations/{id}");
            return await HandleResponseAsync<ApiLocation>(response);
        }

        public async Task<ApiLocation?> CreateLocationAsync(Location location)
        {
            var data = new
            {
                name = location.Name,
                description = location.Description
            };

            var json = JsonConvert.SerializeObject(data);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync($"{_baseUrl}/locations/add", content);

            return await HandleResponseAsync<ApiLocation>(response);
        }

        public async Task<ApiLocation?> UpdateLocationAsync(string apiId, Location location)
        {
            var data = new
            {
                name = location.Name,
                description = location.Description
            };

            var json = JsonConvert.SerializeObject(data);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync($"{_baseUrl}/locations/{apiId}/edit", content);

            return await HandleResponseAsync<ApiLocation>(response);
        }

        public async Task<bool> DeleteLocationAsync(string apiId)
        {
            var response = await _httpClient.PostAsync($"{_baseUrl}/locations/{apiId}/delete", null);
            return response.IsSuccessStatusCode;
        }

        // Storage Item API methods
        public async Task<List<ApiStorageItem>> GetStorageItemsAsync()
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/items");
            var items = await HandleResponseAsync<List<ApiStorageItem>>(response);
            return items ?? new List<ApiStorageItem>();
        }

        public async Task<ApiStorageItem?> GetStorageItemAsync(string id)
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/items/{id}");
            return await HandleResponseAsync<ApiStorageItem>(response);
        }

        public async Task<ApiStorageItem?> CreateStorageItemAsync(StorageItem item, string locationApiId)
        {
            var data = new
            {
                name = item.Name,
                brand = item.Brand,
                size = item.Size,
                nutritional_info = item.NutritionalInfo,
                date_purchased = item.DatePurchased,
                expiration_date = item.ExpirationDate,
                ingredients = item.Ingredients,
                other_info = item.OtherInfo,
                location_id = locationApiId
            };

            var json = JsonConvert.SerializeObject(data);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync($"{_baseUrl}/items/add", content);

            return await HandleResponseAsync<ApiStorageItem>(response);
        }

        public async Task<ApiStorageItem?> UpdateStorageItemAsync(string apiId, StorageItem item, string locationApiId)
        {
            var data = new
            {
                name = item.Name,
                brand = item.Brand,
                size = item.Size,
                nutritional_info = item.NutritionalInfo,
                date_purchased = item.DatePurchased,
                expiration_date = item.ExpirationDate,
                ingredients = item.Ingredients,
                other_info = item.OtherInfo,
                location_id = locationApiId
            };

            var json = JsonConvert.SerializeObject(data);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync($"{_baseUrl}/items/{apiId}/edit", content);

            return await HandleResponseAsync<ApiStorageItem>(response);
        }

        public async Task<bool> DeleteStorageItemAsync(string apiId)
        {
            var response = await _httpClient.PostAsync($"{_baseUrl}/items/{apiId}/delete", null);
            return response.IsSuccessStatusCode;
        }

        // Test connectivity
        public async Task<bool> TestConnectionAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync($"{_baseUrl}/");
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }
    }

    // API response models
    public class ApiLocation
    {
        [JsonProperty("_id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("user_id")]
        public string UserId { get; set; } = string.Empty;
    }

    public class ApiStorageItem
    {
        [JsonProperty("_id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("brand")]
        public string Brand { get; set; } = string.Empty;

        [JsonProperty("size")]
        public string Size { get; set; } = string.Empty;

        [JsonProperty("nutritional_info")]
        public string NutritionalInfo { get; set; } = string.Empty;

        [JsonProperty("date_purchased")]
        public string DatePurchased { get; set; } = string.Empty;

        [JsonProperty("expiration_date")]
        public string ExpirationDate { get; set; } = string.Empty;

        [JsonProperty("ingredients")]
        public string Ingredients { get; set; } = string.Empty;

        [JsonProperty("other_info")]
        public string OtherInfo { get; set; } = string.Empty;

        [JsonProperty("location_id")]
        public string LocationId { get; set; } = string.Empty;

        [JsonProperty("user_id")]
        public string UserId { get; set; } = string.Empty;
    }
}
