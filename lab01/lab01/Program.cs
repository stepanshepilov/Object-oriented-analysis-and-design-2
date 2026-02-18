using lab01.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors(options => {
    options.AddDefaultPolicy(policy => {
        policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader();
    });
});

var app = builder.Build();
app.UseCors();

var wells = new List<Well>();

if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.Use(async (context, next) =>
{
    Console.WriteLine($"Запрос: {context.Request.Path}");
    await next();
});

app.MapGet("/api/wells", () => wells);

app.MapPost("/api/wells", (Well input) => {
    input.Id = Guid.NewGuid();
    input.CreatedAt = DateTime.Now;
    wells.Add(input);
    return Results.Created($"/api/wells/{input.Id}", input);
});

app.MapPut("/api/wells/{id}", (Guid id, Well updatedWell) => {
    var index = wells.FindIndex(w => w.Id == id);
    if (index == -1) return Results.NotFound();
    
    updatedWell.Id = id;
    wells[index] = updatedWell;
    return Results.Ok(updatedWell);
});

app.Run();
