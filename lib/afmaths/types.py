from enum import Enum
from typing import NewType
from astronomy_types import Scalar, Vector2D, Vector3D, Velocity

Mass = NewType("Mass", float)
Pressure = NewType("Pressure", float)
Force = NewType("Force", float)
Area = NewType("Area", Scalar)
TransformationMatrix2D = NewType("TransformationMatrix2D", Vector2D[Vector2D[Scalar]])
TransformationMatrix3D = NewType("TransformationMatrix3D", Vector3D[Vector3D[Scalar]])
DeltaV = NewType("DeltaV", Velocity)
EarthCentredInertialFrame = NewType("EarthCentredInertialFrame", Vector3D[Scalar])
Momentum = NewType("Momentum", Scalar)
Force = NewType("Force", Scalar)
Percentage = NewType("Percentage", float)
AngularMomentum = NewType("AngularMomentum", Vector3D[Scalar])
Torque = NewType("Torque", Scalar)
Impulse = NewType("Impulse", Scalar)


class OrbitalDirection(Enum):
    PROGRADE = "prograde"
    RETROGRADE = "retrograde"
    RADIAL = "radial"
    ANTIRADIAl = "antiradial"
    NORMAL = "normal"
    ANTINORMAL = "antinormal"
