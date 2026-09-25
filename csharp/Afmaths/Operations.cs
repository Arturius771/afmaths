namespace Afmaths;

/// <summary>
/// Provides numerical analysis methods.
/// </summary>
class NumericalAnalysis()
{
    /// <summary>
    /// Performs a single iteration of the Newton-Raphson method.
    /// </summary>
    /// <param name="current_estimate">The current estimate of the root.</param>
    /// <param name="auxiliary_value">The value of the function at the current estimate.</param>
    /// <param name="derivative_value">The value of the derivative of the function at the current estimate.</param>
    /// <returns>The next estimate of the root.</returns>
    public double NewtonRaphson(double current_estimate, double auxiliary_value, double derivative_value)
    {
        return current_estimate - auxiliary_value / derivative_value;
    }

    public (T Result, History<T> History) RootSolver<T>(
        Func<T, T> iterationFunction,
        T initialGuess,
        Func<T, T, double> differenceFunction,
        double tolerance = 1e-6,
        int maxIterations = 100
    )
    {
        var history = new History<T>();

        var x = initialGuess;
        var delta = double.PositiveInfinity;

        var iteration = 0;
        history.AddEntry(iteration, x, null);

        while (iteration < maxIterations && Math.Abs(delta) > tolerance)
        {
            var next = iterationFunction(x);

            delta = differenceFunction(next, x);

            iteration++;
            history.AddEntry(iteration, next, delta);

            x = next;
        }

        return (x, history);
    }
}