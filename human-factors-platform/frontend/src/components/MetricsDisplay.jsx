import React from 'react';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

const RiskBadge = ({ level }) => {
  const colors = {
    low: 'bg-green-100 text-green-800 border-green-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    high: 'bg-red-100 text-red-800 border-red-200',
  };

  const icons = {
    low: <CheckCircle className="w-4 h-4" />,
    medium: <Info className="w-4 h-4" />,
    high: <AlertTriangle className="w-4 h-4" />,
  };

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${colors[level]}`}>
      {icons[level]}
      <span className="ml-1 capitalize">{level} Risk</span>
    </span>
  );
};

const MetricCard = ({ title, value, unit, risk, description, optimal }) => {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <h4 className="text-sm font-medium text-gray-700">{title}</h4>
        {risk && <RiskBadge level={risk} />}
      </div>
      <div className="mt-2">
        <span className="text-3xl font-bold text-gray-900">{value}</span>
        {unit && <span className="text-lg text-gray-500 ml-1">{unit}</span>}
      </div>
      {description && (
        <p className="text-xs text-gray-500 mt-2">{description}</p>
      )}
      {optimal !== undefined && (
        <div className="mt-2">
          {optimal ? (
            <span className="text-xs text-green-600 font-medium">✓ Within optimal range</span>
          ) : (
            <span className="text-xs text-red-600 font-medium">⚠ Outside optimal range</span>
          )}
        </div>
      )}
    </div>
  );
};

const MetricsDisplay = ({ metrics }) => {
  // Prepare data for radar chart
  const radarData = [
    {
      metric: 'Neck',
      score: 100 - Math.min(100, (metrics.neck_flexion.angle_degrees / 60) * 100),
    },
    {
      metric: 'Shoulders',
      score: 100 - Math.min(100, metrics.shoulder_elevation.asymmetry_percent * 5),
    },
    {
      metric: 'Elbows',
      score: (metrics.elbow_angles.left_optimal && metrics.elbow_angles.right_optimal) ? 100 : 50,
    },
    {
      metric: 'Wrists',
      score: 100 - Math.min(100, (metrics.wrist_extension.average_deviation / 45) * 100),
    },
    {
      metric: 'Back',
      score: 100 - Math.min(100, (metrics.back_posture.forward_lean_degrees / 60) * 100),
    },
    {
      metric: 'Symmetry',
      score: metrics.body_symmetry.symmetry_score,
    },
  ];

  // Prepare data for bar chart
  const angleData = [
    { name: 'Neck Flexion', angle: metrics.neck_flexion.angle_degrees, threshold: 20 },
    { name: 'Left Elbow', angle: metrics.elbow_angles.left_angle, threshold: 90 },
    { name: 'Right Elbow', angle: metrics.elbow_angles.right_angle, threshold: 90 },
    { name: 'Back Lean', angle: metrics.back_posture.forward_lean_degrees, threshold: 20 },
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Ergonomic Metrics</h2>

      {/* Overall Risk Assessment */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Overall Risk Assessment</h3>
            <p className="text-sm text-gray-600">
              Risk Score: {metrics.risk_assessment.risk_score.toFixed(2)}/3.0
            </p>
          </div>
          <RiskBadge level={metrics.risk_assessment.overall_risk} />
        </div>
        
        {metrics.risk_assessment.risk_factors.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Identified Risk Factors:</h4>
            <ul className="space-y-1">
              {metrics.risk_assessment.risk_factors.map((factor, idx) => (
                <li key={idx} className="text-sm text-gray-600 flex items-start">
                  <AlertTriangle className="w-4 h-4 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" />
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Posture Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <MetricCard
          title="Neck Flexion"
          value={metrics.neck_flexion.angle_degrees.toFixed(1)}
          unit="°"
          risk={metrics.neck_flexion.risk_level}
          description="Forward head posture angle"
        />
        
        <MetricCard
          title="Shoulder Asymmetry"
          value={metrics.shoulder_elevation.asymmetry_percent.toFixed(1)}
          unit="%"
          risk={metrics.shoulder_elevation.risk_level}
          description="Height difference between shoulders"
        />
        
        <MetricCard
          title="Left Elbow Angle"
          value={metrics.elbow_angles.left_angle.toFixed(1)}
          unit="°"
          optimal={metrics.elbow_angles.left_optimal}
          description="Optimal: 70-110°"
        />
        
        <MetricCard
          title="Right Elbow Angle"
          value={metrics.elbow_angles.right_angle.toFixed(1)}
          unit="°"
          optimal={metrics.elbow_angles.right_optimal}
          description="Optimal: 70-110°"
        />
        
        <MetricCard
          title="Wrist Deviation"
          value={metrics.wrist_extension.average_deviation.toFixed(1)}
          unit="°"
          risk={metrics.wrist_extension.risk_level}
          description="Average wrist extension/flexion"
        />
        
        <MetricCard
          title="Back Forward Lean"
          value={metrics.back_posture.forward_lean_degrees.toFixed(1)}
          unit="°"
          risk={metrics.back_posture.risk_level}
          description="Spine deviation from vertical"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Radar Chart */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Posture Quality Overview</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar name="Quality Score" dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
          <p className="text-xs text-gray-500 text-center mt-2">
            Higher scores indicate better posture quality
          </p>
        </div>

        {/* Bar Chart */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Joint Angles</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={angleData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="angle" fill="#3b82f6" name="Measured Angle" />
              <Bar dataKey="threshold" fill="#10b981" name="Target/Threshold" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Body Symmetry */}
      <div className="bg-gray-50 rounded-lg p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Body Symmetry Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900">
              {metrics.body_symmetry.symmetry_score.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Overall Symmetry</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${metrics.body_symmetry.symmetry_score}%` }}
              ></div>
            </div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900">
              {metrics.body_symmetry.shoulder_symmetry.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Shoulder Symmetry</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-green-600 h-2 rounded-full"
                style={{ width: `${metrics.body_symmetry.shoulder_symmetry}%` }}
              ></div>
            </div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900">
              {metrics.body_symmetry.hip_symmetry.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Hip Symmetry</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-purple-600 h-2 rounded-full"
                style={{ width: `${metrics.body_symmetry.hip_symmetry}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Anthropometric Measurements */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Anthropometric Measurements</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-white rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {metrics.measurements.shoulder_breadth_cm.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Shoulder Breadth (cm)</div>
          </div>
          <div className="text-center p-4 bg-white rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {metrics.measurements.torso_height_cm.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Torso Height (cm)</div>
          </div>
          <div className="text-center p-4 bg-white rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {metrics.measurements.arm_length_cm.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Arm Length (cm)</div>
          </div>
          <div className="text-center p-4 bg-white rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {metrics.measurements.leg_length_cm.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Leg Length (cm)</div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      {metrics.risk_assessment.recommendations.length > 0 && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">Recommendations</h3>
          <ul className="space-y-2">
            {metrics.risk_assessment.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start text-sm text-blue-800">
                <CheckCircle className="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default MetricsDisplay;
