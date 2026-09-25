namespace Afmaths;

public class StateVector
{
    public Position Position { get; }
    public Velocity Velocity { get; }

    public StateVector(Position position, Velocity velocity)
    {
        Position = position;
        Velocity = velocity;
    }
}