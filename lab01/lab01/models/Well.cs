namespace lab01.Models;

public class Well
{
    public Guid Id { get; set; }
    public double X { get; set; }
    public double Y { get; set; }
    public double Z { get; set; }
    public double Pressure { get; set; }
    public double Temperature { get; set; }
    public string RockType { get; set; } = string.Empty;
    public bool IsActive { get; set; }
    public DateTime CreatedAt { get; set; }
    public string FieldName { get; set; } = string.Empty;
    public double FlowRate { get; set; }

    public Well() { }

    public Well(double x, double y, double z, double pressure, double temperature, 
                string rockType, bool isActive, DateTime createdAt, 
                string fieldName, double flowRate)
    {
        this.Id = Guid.NewGuid();
        this.X = x;
        this.Y = y;
        this.Z = z;
        this.Pressure = pressure;
        this.Temperature = temperature;
        this.RockType = rockType;
        this.IsActive = isActive;
        this.CreatedAt = createdAt;
        this.FieldName = fieldName;
        this.FlowRate = flowRate;
    }

    public Well Clone() {

    }
}
