# Afmaths C#

C# implementation of `Afmaths`, intended for reuse from Unity and other .NET applications.

The project contains strongly typed mathematical and space-related functionality, including:

- physical values and constants
- orbital elements
- celestial mechanics
- orbital equations
- coordinate and vector calculations

The library is built as a standalone class library and can be consumed independently of Unity.

## Project Structure

```text
csharp/
├── Afmaths/
│   ├── Afmaths.csproj
│   └── ...
│
├── Afmaths.Tests/
│   ├── Afmaths.Tests.csproj
│   └── ...
│
└── Afmaths.slnx
```

`Afmaths` contains the library implementation.

`Afmaths.Tests` contains the xUnit test suite.

## Requirements

- .NET SDK
- currently targeting:

```xml
<TargetFramework>netstandard2.1</TargetFramework>
```

The library targets .NET Standard so that the compiled assembly can be used by Unity.

Check the installed .NET SDK with:

```bash
dotnet --version
```

## Restore Dependencies

From the `csharp` directory:

```bash
dotnet restore
```

## Build

Build the complete solution:

```bash
dotnet build
```

For a release build:

```bash
dotnet build -c Release
```

You can also build only the Afmaths library:

```bash
dotnet build Afmaths/Afmaths.csproj -c Release
```

The compiled library will be produced at:

```text
Afmaths/bin/Release/netstandard2.1/Afmaths.dll
```

## Run Tests

From the `csharp` directory:

```bash
dotnet test
```

Or run the test project directly:

```bash
dotnet test Afmaths.Tests/Afmaths.Tests.csproj
```

A successful run should build both the library and test project before executing the tests.

## Using Afmaths

Reference the project from another .NET project with:

```bash
dotnet add reference ../Afmaths/Afmaths.csproj
```

Then use the library normally:

```csharp
using Afmaths;

var mechanics = new CelestialMechanics();

var radius = new Distance(7_000_000);
var semiMajorAxis = new SemiMajorAxis(7_000_000);

var velocity = mechanics.VisViva(
    CelestialMechanics.EarthGravitationalParameter,
    radius,
    semiMajorAxis
);

Console.WriteLine(velocity.Value);
```

## Unity Integration

Build Afmaths in release mode:

```bash
dotnet build Afmaths/Afmaths.csproj -c Release
```

Then copy:

```text
Afmaths/bin/Release/netstandard2.1/Afmaths.dll
```

into the Unity project:

```text
Assets/Plugins/Afmaths/Afmaths.dll
```

Unity should automatically detect the assembly.

The library can then be imported from Unity scripts:

```csharp
using Afmaths;
```

## Development Workflow

The normal development workflow is:

```text
Edit Afmaths
    ↓
Run tests
    ↓
Build release DLL
    ↓
Copy DLL into Unity
    ↓
Test integration in Unity
```

Typical commands:

```bash
dotnet test
dotnet build Afmaths/Afmaths.csproj -c Release
```

## Notes

The C# project should remain independent of Unity-specific APIs.

This keeps Afmaths reusable as a general C# library while allowing Unity to consume it as a compiled dependency.
