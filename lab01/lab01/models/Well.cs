using System.Text.Json.Serialization;
namespace lab01.Models;

[JsonDerivedType(typeof(ProductionWell), "prod")]
[JsonDerivedType(typeof(InjectionWell), "inj")]

public abstract class BaseWell
{
    public Guid Id { get; set; }
    public double X { get; set; }
    public double Y { get; set; }
    public double Z { get; set; }
    public double Pressure { get; set; }
    public string FieldName { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }

    public BaseWell() { }

    public BaseWell(double x, double y, double z, double pressure, string fieldName)
    {
        Id = Guid.NewGuid();
        X = x; Y = y; Z = z;
        Pressure = pressure;
        FieldName = fieldName;
        CreatedAt = DateTime.Now;
    }
}

public class ProductionWell : BaseWell
{
    public double OilQuality { get; set; }
    public double GasCut { get; set; }

    public ProductionWell() { }
    
    public ProductionWell(double x, double y, double z, double pressure, string fieldName, double oilQuality, double gasCut) 
        : base(x, y, z, pressure, fieldName)
    {
        OilQuality = oilQuality;
        GasCut = gasCut;
    }
}

public class InjectionWell : BaseWell
{
    public double InjectionRate { get; set; }
    public string FluidType { get; set; } = "Water";

    public InjectionWell() { }

    public InjectionWell(double x, double y, double z, double pressure, string fieldName, double injectionRate, string fluidType) 
        : base(x, y, z, pressure, fieldName)
    {
        InjectionRate = injectionRate;
        FluidType = fluidType;
    }
}
