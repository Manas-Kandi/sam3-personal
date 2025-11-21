import React, { useState } from 'react';
import { Brain, FileText, AlertTriangle, TrendingUp, Shield, ChevronDown, ChevronUp } from 'lucide-react';

const InsightsDisplay = ({ insights }) => {
  const [expandedSections, setExpandedSections] = useState({
    executive: true,
    findings: false,
    risk: false,
    recommendations: true,
    compliance: false,
    metrics: false,
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const SectionHeader = ({ icon: Icon, title, section, color }) => (
    <button
      onClick={() => toggleSection(section)}
      className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors rounded-lg"
    >
      <div className="flex items-center">
        <Icon className={`w-5 h-5 ${color} mr-3`} />
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      {expandedSections[section] ? (
        <ChevronUp className="w-5 h-5 text-gray-400" />
      ) : (
        <ChevronDown className="w-5 h-5 text-gray-400" />
      )}
    </button>
  );

  const formatText = (text) => {
    if (!text) return null;
    
    // Split by lines and format
    const lines = text.split('\n').filter(line => line.trim());
    
    return lines.map((line, idx) => {
      // Check if it's a header (starts with ##, ###, etc.)
      if (line.trim().startsWith('#')) {
        const headerText = line.replace(/^#+\s*/, '');
        return (
          <h4 key={idx} className="font-semibold text-gray-900 mt-4 mb-2">
            {headerText}
          </h4>
        );
      }
      
      // Check if it's a list item
      if (line.trim().match(/^[-*]\s/)) {
        const itemText = line.replace(/^[-*]\s*/, '');
        return (
          <li key={idx} className="ml-4 text-gray-700 mb-1">
            {itemText}
          </li>
        );
      }
      
      // Check if it's numbered list
      if (line.trim().match(/^\d+\.\s/)) {
        const itemText = line.replace(/^\d+\.\s*/, '');
        return (
          <li key={idx} className="ml-4 text-gray-700 mb-1">
            {itemText}
          </li>
        );
      }
      
      // Regular paragraph
      if (line.trim()) {
        return (
          <p key={idx} className="text-gray-700 mb-2">
            {line}
          </p>
        );
      }
      
      return null;
    });
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <div className="flex items-center mb-6">
        <Brain className="w-8 h-8 text-purple-600 mr-3" />
        <h2 className="text-2xl font-bold text-gray-900">AI-Powered Ergonomic Insights</h2>
      </div>

      <div className="space-y-4">
        {/* Executive Summary */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <SectionHeader
            icon={FileText}
            title="Executive Summary"
            section="executive"
            color="text-blue-600"
          />
          {expandedSections.executive && (
            <div className="p-6 bg-blue-50 border-t border-gray-200">
              <div className="prose max-w-none">
                {formatText(insights.executive_summary)}
              </div>
              
              {insights.summary_stats && (
                <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white rounded-lg p-3 text-center">
                    <div className="text-2xl font-bold text-gray-900 capitalize">
                      {insights.summary_stats.overall_risk}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">Overall Risk</div>
                  </div>
                  <div className="bg-white rounded-lg p-3 text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {insights.summary_stats.risk_score?.toFixed(2)}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">Risk Score</div>
                  </div>
                  <div className="bg-white rounded-lg p-3 text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {insights.summary_stats.num_risk_factors}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">Risk Factors</div>
                  </div>
                  <div className="bg-white rounded-lg p-3 text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {insights.summary_stats.symmetry_score?.toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-600 mt-1">Symmetry</div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Detailed Findings */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <SectionHeader
            icon={TrendingUp}
            title="Detailed Findings"
            section="findings"
            color="text-green-600"
          />
          {expandedSections.findings && (
            <div className="p-6 bg-gray-50 border-t border-gray-200">
              <div className="prose max-w-none">
                {formatText(insights.detailed_findings)}
              </div>
            </div>
          )}
        </div>

        {/* Risk Analysis */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <SectionHeader
            icon={AlertTriangle}
            title="Risk Analysis"
            section="risk"
            color="text-red-600"
          />
          {expandedSections.risk && (
            <div className="p-6 bg-red-50 border-t border-gray-200">
              <div className="prose max-w-none">
                {formatText(insights.risk_analysis)}
              </div>
            </div>
          )}
        </div>

        {/* Recommendations */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <SectionHeader
            icon={FileText}
            title="Prioritized Recommendations"
            section="recommendations"
            color="text-purple-600"
          />
          {expandedSections.recommendations && (
            <div className="p-6 bg-purple-50 border-t border-gray-200">
              <div className="prose max-w-none">
                {formatText(insights.recommendations)}
              </div>
            </div>
          )}
        </div>

        {/* Compliance Assessment */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <SectionHeader
            icon={Shield}
            title="Compliance Assessment"
            section="compliance"
            color="text-yellow-600"
          />
          {expandedSections.compliance && (
            <div className="p-6 bg-yellow-50 border-t border-gray-200">
              <div className="prose max-w-none">
                {formatText(insights.compliance_assessment)}
              </div>
            </div>
          )}
        </div>

        {/* Metrics Summary */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <SectionHeader
            icon={TrendingUp}
            title="Quantitative Metrics Summary"
            section="metrics"
            color="text-indigo-600"
          />
          {expandedSections.metrics && (
            <div className="p-6 bg-indigo-50 border-t border-gray-200">
              <div className="prose max-w-none">
                {formatText(insights.metrics_summary)}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Full Analysis (Collapsible) */}
      <details className="mt-6 bg-gray-50 rounded-lg p-4">
        <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
          View Full Analysis Text
        </summary>
        <div className="mt-4 p-4 bg-white rounded border border-gray-200">
          <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
            {insights.full_analysis}
          </pre>
        </div>
      </details>

      {/* Disclaimer */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-xs text-yellow-800">
          <strong>Disclaimer:</strong> This AI-generated analysis is based on computer vision measurements
          and should be used as a supplementary tool for Human Factors research. Always consult with
          qualified ergonomics professionals for comprehensive workplace assessments and interventions.
        </p>
      </div>
    </div>
  );
};

export default InsightsDisplay;
