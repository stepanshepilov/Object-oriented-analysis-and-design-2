using lab01.Models;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddCors(opt => opt.AddDefaultPolicy(p => p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));
var app = builder.Build();
app.UseCors();

var wells = new List<BaseWell>();

app.MapGet("/api/wells", () => wells);

app.MapPost("/api/wells", (WellRequest req) => {
    BaseWell newWell;

    if (req.Type == "prod") {
        newWell = new ProductionWell(req.X, req.Y, req.Z, req.Pressure, req.FieldName, req.OilQuality, req.GasCut);
    } else {
        newWell = new InjectionWell(req.X, req.Y, req.Z, req.Pressure, req.FieldName, req.InjectionRate, req.FluidType);
    }

    wells.Add(newWell);
    return Results.Created($"/api/wells/{newWell.Id}", newWell);
});

app.Run();

public record WellRequest(string Type, double X, double Y, double Z, double Pressure, string FieldName, 
                          double OilQuality, double GasCut, double InjectionRate, string FluidType);
