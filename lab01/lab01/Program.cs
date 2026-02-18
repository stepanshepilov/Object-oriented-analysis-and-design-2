using lab01.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors(opt => opt.AddDefaultPolicy(p => 
    p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));

var app = builder.Build();
app.UseCors();

var wells = new List<BaseWell>();

app.MapGet("/api/wells", () => wells);

app.MapPost("/api/wells", (BaseWell newWell) => {
    newWell.Id = Guid.NewGuid();
    newWell.CreatedAt = DateTime.Now;
    
    wells.Add(newWell);
    return Results.Created($"/api/wells/{newWell.Id}", newWell);
});

app.MapPost("/api/wells/{id}/clone", (Guid id, CloneRequest req) => {
    var original = wells.FirstOrDefault(w => w.Id == id);
    if (original == null) return Results.NotFound();

    var clonedWell = original.Clone();
    
    clonedWell.X = req.X;
    clonedWell.Y = req.Y;
    
    wells.Add(clonedWell);
    return Results.Created($"/api/wells/{clonedWell.Id}", clonedWell);
});

app.Run();

public record CloneRequest(double X, double Y);
