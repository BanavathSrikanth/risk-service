using System.Text.Json.Serialization;

namespace DotNetBff.Models;

public class BffRiskCalculationRequest
{
    public string AssetId { get; set; } = "POLE-88421";
    public string TenantId { get; set; } = "PACIFIC-POWER";
    public double AgeYears { get; set; } = 25.0;
    public string Material { get; set; } = "wood";
    public double RemainingFiberPct { get; set; } = 65.0;
    public string DefectSeverity { get; set; } = "major";
    public double LeanDeg { get; set; } = 5.0;
    public int AttachmentCount { get; set; } = 4;
    public string AssetClass { get; set; } = "distribution";
    public bool ReinforcedWithin10Years { get; set; } = false;

    // Consequence
    public double PopulationExposure { get; set; } = 75.0;
    public double CriticalInfrastructure { get; set; } = 60.0;
    public double ServiceImpact { get; set; } = 70.0;

    // Financial Exposure (CQS)
    public double FailureCost { get; set; } = 450000.0;
    public double OutageDurationHours { get; set; } = 24.0;
    public int CustomerCount { get; set; } = 3500;

    // Weather (DHM)
    public double WindSpeedMph { get; set; } = 42.0;
    public double TemperatureF { get; set; } = 98.0;
    public double RelativeHumidityPct { get; set; } = 18.0;
    public double PrecipitationIn { get; set; } = 0.0;
    public double? FireWeatherIndex { get; set; } = 75.0;

    // Operational
    public double DaysOverdue { get; set; } = 45.0;
    public bool WorkAlreadyScheduled { get; set; } = false;
}

public class BffFinancialEngineRequest
{
    public string AssetId { get; set; } = "POLE-88421";
    public string TenantId { get; set; } = "PACIFIC-POWER";
    public string ConditionBand { get; set; } = "POOR";
    public double ReplacementCost { get; set; } = 125000.0;
    public int Customers { get; set; } = 3500;
    public double OutageHours { get; set; } = 24.0;
    public double OutageCostPerCustomerHour { get; set; } = 15.0;
    public double WildfireLiabilityExposure { get; set; } = 5000000.0;
    public string HftdTier { get; set; } = "Tier3";
    public double ActionCost { get; set; } = 35000.0;
    public double RemainingLife { get; set; } = 3.0;
    public double DesignLife { get; set; } = 40.0;
    public double DiscountRate { get; set; } = 0.07;
    public double DegradationRate { get; set; } = 0.05;
}

public class BffPolePriorityRequest
{
    public string AssetId { get; set; } = "POLE-88421";
    public string TenantId { get; set; } = "PACIFIC-POWER";
    public double CompositeRiskScore { get; set; } = 82.5;
    public double ConsequenceScore { get; set; } = 78.0;
    public double HazardExposureScore { get; set; } = 85.0;
    public double DaysOverdue { get; set; } = 45.0;
    public double InspectionConfidence { get; set; } = 0.9;
}

public class BffUnifiedAuditRequest
{
    public string AssetId { get; set; } = "POLE-88421";
    public string TenantId { get; set; } = "PACIFIC-POWER";
    public BffRiskCalculationRequest? RiskParams { get; set; }
    public BffFinancialEngineRequest? FinancialParams { get; set; }
}

public class BffEnrichedRiskResponse
{
    public string RiskEvaluationId { get; set; } = string.Empty;
    public string AssetId { get; set; } = string.Empty;
    public string TenantId { get; set; } = string.Empty;
    public double RiskScore { get; set; }
    public string RiskCategory { get; set; } = string.Empty;
    public string CategoryColor { get; set; } = string.Empty;
    public string ActionRecommendation { get; set; } = string.Empty;
    public double Confidence { get; set; } = 1.0;
    public string CalculatedAt { get; set; } = string.Empty;
    public Dictionary<string, double> FactorScores { get; set; } = new();
    public List<object> Drivers { get; set; } = new();
    public List<string> Warnings { get; set; } = new();
}

public class BffEnrichedFinancialResponse
{
    public string EvaluationId { get; set; } = string.Empty;
    public string AssetId { get; set; } = string.Empty;
    public string TenantId { get; set; } = string.Empty;
    public string CalculationVersion { get; set; } = "1.0";
    public object Scenarios { get; set; } = new();
    public object BaseSummary { get; set; } = new();
    public string InvestmentRecommendation { get; set; } = string.Empty;
    public string FormattedNetBenefit { get; set; } = string.Empty;
    public string FormattedRoi { get; set; } = string.Empty;
    public string FormattedEal { get; set; } = string.Empty;
}

public class BffEnrichedPriorityResponse
{
    public string AssetId { get; set; } = string.Empty;
    public string TenantId { get; set; } = string.Empty;
    public double PriorityScore { get; set; }
    public string PriorityTier { get; set; } = string.Empty;
    public string PriorityColor { get; set; } = string.Empty;
    public string UrgencyRecommendation { get; set; } = string.Empty;
    public Dictionary<string, object> ScoreBreakdown { get; set; } = new();
}

public class BffUnifiedAuditResponse
{
    public string AssetId { get; set; } = string.Empty;
    public string TenantId { get; set; } = string.Empty;
    public string Timestamp { get; set; } = string.Empty;
    public BffEnrichedRiskResponse? Risk { get; set; }
    public BffEnrichedFinancialResponse? Financials { get; set; }
    public BffEnrichedPriorityResponse? Priority { get; set; }
    public int HistoryCount { get; set; } = 0;
    public string OverallHealthStatus { get; set; } = "STABLE";
}
