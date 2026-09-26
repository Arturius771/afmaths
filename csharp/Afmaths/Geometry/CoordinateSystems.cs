namespace Afmaths;

public class Latitude(double value) : PhysicalValue<Latitude>(value)
{
    protected override Latitude Create(double value) => new(value);
}