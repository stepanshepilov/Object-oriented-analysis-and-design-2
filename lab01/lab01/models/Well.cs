using System.Text.Json.Serialization;
namespace lab01.Models;

[JsonDerivedType(typeof(ProductionWell), "prod")]
[JsonDerivedType(typeof(InjectionWell), "inj")]
[JsonPolymorphic(TypeDiscriminatorPropertyName = "type")]

public abstract class BaseWell
{
    public Guid Id { get; set; }

    [JsonIgnore]
    public string Type { get; set; } = string.Empty;
    public double X { get; set; }
    public double Y { get; set; }
    public double Z { get; set; }
    public double Pressure { get; set; }
    public string FieldName { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }

    public BaseWell() { }

    protected BaseWell(BaseWell source)
    {
        this.Id = Guid.NewGuid();
        this.Z = source.Z;
        this.Pressure = source.Pressure;
        this.FieldName = source.FieldName + " (Clone)";
        this.Type = source.Type;
        this.CreatedAt = DateTime.Now;
    }

    public abstract BaseWell Clone();
}

public class ProductionWell : BaseWell
{
    public double OilQuality { get; set; }
    public double GasCut { get; set; }

    public ProductionWell() { Type = "prod"; }

    public ProductionWell(ProductionWell source) : base(source)
    {
        this.OilQuality = source.OilQuality;
        this.GasCut = source.GasCut;
    }

    public override BaseWell Clone()
    {
        return new ProductionWell(this);
    }
}

public class InjectionWell : BaseWell
{
    public double InjectionRate { get; set; }
    public string FluidType { get; set; } = "Water";

    public InjectionWell() { Type = "inj"; }

    public InjectionWell(InjectionWell source) : base(source)
    {
        this.InjectionRate = source.InjectionRate;
        this.FluidType = source.FluidType;
    }

    public override BaseWell Clone()
    {
        return new InjectionWell(this);
    }
}
