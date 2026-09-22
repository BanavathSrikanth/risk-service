using System.Text.Json;
using DotNetBff.Models;
using DotNetBff.Services;
using Microsoft.AspNetCore.Http.Json;

var builder = WebApplication.CreateBuilder(args);

// Configure ASP.NET Core to listen on port 8001
builder.WebHost.UseUrls("http://localhost:8001");

// Register CORS for React Frontend (running on port 3000 / 5173 / localhost)
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReactApp", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

// Configure JSON serialization to use snake_case property names for React UI compatibility
builder.Services.Configure<JsonOptions>(options =>
{
    options.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
    options.SerializerOptions.PropertyNameCaseInsensitive = true;
});

// Configure HttpClient for downstream Python Risk Backend Service (port 8000)
string backendUrl = Environment.GetEnvironmentVariable("BACKEND_SERVICE_URL") ?? "http://localhost:8000";
builder.Services.AddHttpClient<BffService>(client =>
{
    client.BaseAddress = new Uri(backendUrl);
    client.Timeout = TimeSpan.FromSeconds(15);
});

var app = builder.Build();

app.UseCors("AllowReactApp");

// Health Check Endpoint for React Frontend
app.MapGet("/bff/health", async (BffService bffService) =>
{
    string backendStatus = await bffService.CheckBackendHealthAsync();
    return Results.Ok(new
    {
        status = "healthy",
        service = "dotnet-10-bff-service",
        port = 8001,
        backend_url = backendUrl,
        backend_status = backendStatus
    });
});

// Risk Calculation Button Endpoint
app.MapPost("/bff/api/v1/calculate-risk", async (BffRiskCalculationRequest request, BffService bffService) =>
{
    try
    {
        var result = await bffService.CalculateRiskAsync(request);
        return Results.Ok(result);
    }
    catch (Exception ex)
    {
        return Results.Problem(detail: $"BFF error: {ex.Message}", statusCode: 500);
    }
});

// Financial Engine Evaluation Button Endpoint
app.MapPost("/bff/api/v1/evaluate-financials", async (BffFinancialEngineRequest request, BffService bffService) =>
{
    try
    {
        var result = await bffService.EvaluateFinancialsAsync(request);
        return Results.Ok(result);
    }
    catch (Exception ex)
    {
        return Results.Problem(detail: $"BFF error: {ex.Message}", statusCode: 500);
    }
});

// Pole Work Priority Button Endpoint
app.MapPost("/bff/api/v1/pole-priority", async (BffPolePriorityRequest request, BffService bffService) =>
{
    try
    {
        var result = await bffService.CalculatePolePriorityAsync(request);
        return Results.Ok(result);
    }
    catch (Exception ex)
    {
        return Results.Problem(detail: $"BFF error: {ex.Message}", statusCode: 500);
    }
});

// Comprehensive Unified Asset Audit Button Endpoint
app.MapPost("/bff/api/v1/asset-risk-summary", async (BffUnifiedAuditRequest request, BffService bffService) =>
{
    try
    {
        var result = await bffService.RunUnifiedAuditAsync(request.AssetId, request.TenantId);
        return Results.Ok(result);
    }
    catch (Exception ex)
    {
        return Results.Problem(detail: $"Unified audit error: {ex.Message}", statusCode: 500);
    }
});

app.Run();
