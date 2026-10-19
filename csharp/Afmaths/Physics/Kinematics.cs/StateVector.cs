namespace Afmaths;

/// <summary>
/// Represents the state of an object in terms of its position and velocity.
/// </summary>
/// <param name="position">The position of the object.</param>
/// <param name="velocity">The velocity of the object.</param>
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