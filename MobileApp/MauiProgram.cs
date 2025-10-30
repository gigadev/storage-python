﻿using Microsoft.Extensions.Logging;
using StorageTrackerMaui.Data;
using StorageTrackerMaui.Services;

namespace StorageTrackerMaui;

public static class MauiProgram
{
	public static MauiApp CreateMauiApp()
	{
		var builder = MauiApp.CreateBuilder();
		builder
			.UseMauiApp<App>()
			.ConfigureFonts(fonts =>
			{
				fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
			});

		builder.Services.AddMauiBlazorWebView();

#if DEBUG
		builder.Services.AddBlazorWebViewDeveloperTools();
		builder.Logging.AddDebug();
#endif

		// Register services
		builder.Services.AddSingleton<DatabaseService>();
		builder.Services.AddSingleton<ApiClient>();
		builder.Services.AddSingleton<AuthService>();
		builder.Services.AddSingleton<SyncService>();

		// Build and initialize
		var app = builder.Build();

		// Initialize database on startup
		var dbService = app.Services.GetRequiredService<DatabaseService>();
		Task.Run(async () => await dbService.InitializeAsync()).Wait();

		return app;
	}
}
