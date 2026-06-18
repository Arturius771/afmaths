using System;
using UnityEngine;

public class BezierCurveControllerBase : MonoBehaviour {

    
    [Range(0.0f, 1.0f)]
    [SerializeField] protected float timeOrPointOnCurve;
    
    protected Vector3 GetPointOnBezierCurve(Vector3 startPoint, Vector3 controlPoint1, Vector3 controlPoint2, Vector3 target, float t) {
        Vector3[] lines = GetInterpolations(startPoint, controlPoint1, controlPoint2, target, t);
        Vector3 pointOnCurve = Lerp(lines[lines.Length - 2], lines[lines.Length - 1], t);

        return pointOnCurve;
    }   

    protected void DrawCurve(Vector3 startPoint, Vector3 controlPoint1, Vector3 controlPoint2, Vector3 target, float resolution = 20f, bool drawLinesToControlPoints = false)
    {
        Vector3 previousPoint = startPoint;

        for(int i = 0; i < resolution; i++) {
            Vector3 currentPoint = GetPointOnBezierCurve(startPoint, controlPoint1, controlPoint2, target, i/resolution);
            Debug.DrawLine(previousPoint, currentPoint, Color.red);
            previousPoint = currentPoint;
        }

        if (!drawLinesToControlPoints) return;
        
        Vector3[] lines = GetInterpolations(startPoint, controlPoint1, controlPoint2, target, timeOrPointOnCurve);

        Debug.DrawLine(startPoint, controlPoint1, Color.green);     
        Debug.DrawLine(controlPoint1, controlPoint2, Color.green);     
        Debug.DrawLine(controlPoint2, target, Color.green);  
        Debug.DrawLine(lines[0], lines[1], Color.green);   
        Debug.DrawLine(lines[1], lines[2], Color.green);   
        Debug.DrawLine(lines[3], lines[4], Color.green);   
    }

    private Vector3[] GetInterpolations(Vector3 startPoint, Vector3 controlPoint1, Vector3 controlPoint2, Vector3 target, float t)
    {
        Vector3 a = Lerp(startPoint, controlPoint1, t);
        Vector3 b = Lerp(controlPoint1, controlPoint2, t);
        Vector3 c = Lerp(controlPoint2, target, t);
        Vector3 d = Lerp(a, b, t);
        Vector3 e = Lerp(b, c, t);

        return new Vector3[] { a, b, c, d, e };
    }
    private Vector3 Lerp(Vector3 a, Vector3 b, float t) { 
        return (1f - t) * a + t * b;
    }
}