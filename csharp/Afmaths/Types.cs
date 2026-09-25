namespace Afmaths;

/// <summary>
/// Represents the history of iterations for a numerical method.
/// </summary>
/// <typeparam name="T">The type of the value being tracked in the history.</typeparam>
public class History<T>
{
    public List<(int Iteration, T Value, double? Delta)> Entries { get; } = new List<(int Iteration, T Value, double? Delta)>();

    public void AddEntry(int iteration, T value, double? delta)
    {
        Entries.Add((iteration, value, delta));
    }
}