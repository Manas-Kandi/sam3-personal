# Copyright (c) 2025 Human Factors Platform
"""
LLM-Powered Ergonomic Insights Generator
Integrates with SAM 3D Body metrics to generate comprehensive analysis
"""

import os
from typing import Dict, Any, List
import json
from anthropic import Anthropic
from openai import OpenAI


class LLMErgonomicAnalyzer:
    """
    Generates comprehensive ergonomic insights using LLM based on actual metrics
    from SAM 3D Body analysis.
    """
    
    def __init__(self, provider: str = "anthropic", api_key: str = None):
        """
        Initialize LLM analyzer.
        
        Args:
            provider: "anthropic", "openai", or "nvidia"
            api_key: API key for the provider (or set via environment variable)
        """
        self.provider = provider
        
        if provider == "anthropic":
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.model = "claude-3-5-sonnet-20241022"
        elif provider == "openai":
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4o"
        elif provider == "nvidia":
            self.client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=api_key or os.getenv("NVIDIA_API_KEY")
            )
            self.model = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
        else:
            raise ValueError(f"Unsupported provider: {provider}. Choose 'anthropic', 'openai', or 'nvidia'")
    
    def generate_insights(self, ergonomic_metrics: Dict[str, Any], image_context: str = "") -> Dict[str, Any]:
        """
        Generate comprehensive ergonomic insights from metrics.
        
        Args:
            ergonomic_metrics: Dictionary of metrics from ErgonomicAnalyzer
            image_context: Optional context about the image (e.g., "office worker at desk")
        
        Returns:
            Dictionary with structured insights
        """
        # Create structured prompt with actual metrics
        prompt = self._create_analysis_prompt(ergonomic_metrics, image_context)
        
        # Get LLM response
        if self.provider == "anthropic":
            response = self._query_anthropic(prompt)
        elif self.provider in ["openai", "nvidia"]:
            response = self._query_openai(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        # Parse and structure the response
        insights = self._parse_insights(response, ergonomic_metrics)
        
        return insights
    
    def _create_analysis_prompt(self, metrics: Dict[str, Any], context: str) -> str:
        """Create detailed prompt with actual metrics for LLM analysis."""
        
        prompt = f"""You are an expert Human Factors researcher and ergonomist analyzing workplace posture data.

You have been provided with precise 3D body measurements from a computer vision analysis. Your task is to provide a comprehensive ergonomic assessment based on these ACTUAL MEASUREMENTS.

## Context
{context if context else "Workplace posture analysis"}

## Measured Ergonomic Metrics

### Neck Posture
- Forward flexion angle: {metrics['neck_flexion']['angle_degrees']:.1f}°
- Risk level: {metrics['neck_flexion']['risk_level']}
- Reference: Optimal is <20°, concerning at >45°

### Shoulder Position
- Asymmetry: {metrics['shoulder_elevation']['asymmetry_percent']:.1f}%
- Left shoulder height: {metrics['shoulder_elevation']['left_height']:.3f}m
- Right shoulder height: {metrics['shoulder_elevation']['right_height']:.3f}m
- Risk level: {metrics['shoulder_elevation']['risk_level']}

### Elbow Angles
- Left elbow: {metrics['elbow_angles']['left_angle']:.1f}°
- Right elbow: {metrics['elbow_angles']['right_angle']:.1f}°
- Left optimal: {metrics['elbow_angles']['left_optimal']}
- Right optimal: {metrics['elbow_angles']['right_optimal']}
- Reference: Optimal range is 70-110°

### Wrist Position
- Left deviation: {metrics['wrist_extension']['left_deviation']:.1f}°
- Right deviation: {metrics['wrist_extension']['right_deviation']:.1f}°
- Average deviation: {metrics['wrist_extension']['average_deviation']:.1f}°
- Risk level: {metrics['wrist_extension']['risk_level']}

### Back/Spine Posture
- Forward lean: {metrics['back_posture']['forward_lean_degrees']:.1f}°
- Risk level: {metrics['back_posture']['risk_level']}
- Reference: Optimal is <20°, high risk at >45°

### Body Symmetry
- Overall symmetry score: {metrics['body_symmetry']['symmetry_score']:.1f}/100
- Shoulder symmetry: {metrics['body_symmetry']['shoulder_symmetry']:.1f}/100
- Hip symmetry: {metrics['body_symmetry']['hip_symmetry']:.1f}/100

### Anthropometric Measurements
- Shoulder breadth: {metrics['measurements']['shoulder_breadth_cm']:.1f} cm
- Torso height: {metrics['measurements']['torso_height_cm']:.1f} cm
- Arm length: {metrics['measurements']['arm_length_cm']:.1f} cm
- Leg length: {metrics['measurements']['leg_length_cm']:.1f} cm

### Overall Risk Assessment
- Risk level: {metrics['risk_assessment']['overall_risk']}
- Risk score: {metrics['risk_assessment']['risk_score']:.2f}/3.0
- Identified risk factors: {', '.join(metrics['risk_assessment']['risk_factors']) if metrics['risk_assessment']['risk_factors'] else 'None'}

## Required Analysis

Please provide a comprehensive ergonomic assessment in the following structured format:

1. **Executive Summary** (2-3 sentences)
   - Overall posture quality
   - Primary concerns
   - Urgency level

2. **Detailed Findings** (organized by body region)
   - Head/Neck analysis with specific angle references
   - Shoulder/Upper back analysis
   - Arms/Elbows analysis
   - Wrists/Hands analysis
   - Lower back/Spine analysis
   - Body symmetry assessment

3. **Risk Analysis**
   - Immediate risks (if any)
   - Long-term health implications
   - Specific injury risks (e.g., RSI, neck strain, lower back pain)

4. **Prioritized Recommendations** (in order of importance)
   - Immediate adjustments needed
   - Equipment modifications
   - Behavioral changes
   - Long-term considerations

5. **Compliance Assessment**
   - OSHA ergonomic guidelines compliance
   - ISO 11226 (static working postures) compliance
   - Any relevant standards violations

6. **Quantitative Metrics Summary**
   - Key measurements that need attention
   - Target values for improvement
   - Measurable goals

Base your analysis STRICTLY on the provided measurements. Be specific, cite the actual numbers, and provide actionable insights suitable for Human Factors research documentation.
"""
        
        return prompt
    
    def _query_anthropic(self, prompt: str) -> str:
        """Query Anthropic Claude API."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for more consistent, factual analysis
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    
    def _query_openai(self, prompt: str) -> str:
        """Query OpenAI API (also works for NVIDIA NIM with OpenAI-compatible interface)."""
        # NVIDIA NIM uses OpenAI-compatible API with streaming support
        if self.provider == "nvidia":
            # Use streaming for NVIDIA as shown in the example
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Human Factors researcher and ergonomist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # NVIDIA recommended temperature
                top_p=0.7,        # NVIDIA recommended top_p
                max_tokens=2048,  # Increased for comprehensive analysis
                stream=True
            )
            
            # Collect streamed response
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
            
            return full_response
        else:
            # Standard OpenAI non-streaming
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Human Factors researcher and ergonomist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
    
    def _parse_insights(self, llm_response: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured insights."""
        
        # Extract sections from the response
        sections = {
            'executive_summary': '',
            'detailed_findings': '',
            'risk_analysis': '',
            'recommendations': '',
            'compliance_assessment': '',
            'metrics_summary': '',
            'full_analysis': llm_response
        }
        
        # Simple section extraction (can be enhanced with more sophisticated parsing)
        lines = llm_response.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower()
            if 'executive summary' in line_lower:
                current_section = 'executive_summary'
            elif 'detailed findings' in line_lower:
                current_section = 'detailed_findings'
            elif 'risk analysis' in line_lower:
                current_section = 'risk_analysis'
            elif 'recommendations' in line_lower or 'prioritized recommendations' in line_lower:
                current_section = 'recommendations'
            elif 'compliance' in line_lower:
                current_section = 'compliance_assessment'
            elif 'metrics summary' in line_lower or 'quantitative' in line_lower:
                current_section = 'metrics_summary'
            elif current_section and line.strip():
                sections[current_section] += line + '\n'
        
        # Add raw metrics for reference
        sections['raw_metrics'] = metrics
        
        # Generate summary statistics
        sections['summary_stats'] = {
            'overall_risk': metrics['risk_assessment']['overall_risk'],
            'risk_score': metrics['risk_assessment']['risk_score'],
            'num_risk_factors': len(metrics['risk_assessment']['risk_factors']),
            'symmetry_score': metrics['body_symmetry']['symmetry_score'],
            'primary_concerns': metrics['risk_assessment']['risk_factors'][:3] if metrics['risk_assessment']['risk_factors'] else []
        }
        
        return sections
    
    def generate_comparative_analysis(self, 
                                     current_metrics: Dict[str, Any],
                                     previous_metrics: List[Dict[str, Any]],
                                     time_period: str = "over time") -> Dict[str, Any]:
        """
        Generate comparative analysis across multiple measurements.
        
        Args:
            current_metrics: Current ergonomic metrics
            previous_metrics: List of previous measurements
            time_period: Description of time period
        
        Returns:
            Comparative analysis insights
        """
        
        prompt = f"""You are analyzing ergonomic posture changes {time_period}.

## Current Measurement
{json.dumps(current_metrics, indent=2)}

## Previous Measurements
{json.dumps(previous_metrics, indent=2)}

Provide a comparative analysis focusing on:
1. Trends in posture quality (improving/declining)
2. Specific metrics that have changed significantly
3. Effectiveness of previous recommendations
4. Updated recommendations based on trends
5. Long-term health trajectory

Be specific with numbers and cite actual measurements.
"""
        
        if self.provider == "anthropic":
            response = self._query_anthropic(prompt)
        else:
            response = self._query_openai(prompt)
        
        return {
            'comparative_analysis': response,
            'current_metrics': current_metrics,
            'previous_metrics': previous_metrics,
            'time_period': time_period
        }
    
    def generate_research_summary(self, 
                                 metrics_list: List[Dict[str, Any]],
                                 study_context: str = "") -> str:
        """
        Generate research-grade summary for multiple subjects/measurements.
        
        Args:
            metrics_list: List of ergonomic metrics from multiple subjects
            study_context: Context about the research study
        
        Returns:
            Research summary suitable for publication
        """
        
        # Calculate aggregate statistics
        total_subjects = len(metrics_list)
        high_risk_count = sum(1 for m in metrics_list if m['risk_assessment']['overall_risk'] == 'high')
        medium_risk_count = sum(1 for m in metrics_list if m['risk_assessment']['overall_risk'] == 'medium')
        
        avg_neck_flexion = sum(m['neck_flexion']['angle_degrees'] for m in metrics_list) / total_subjects
        avg_symmetry = sum(m['body_symmetry']['symmetry_score'] for m in metrics_list) / total_subjects
        
        prompt = f"""You are writing a research summary for a Human Factors study.

## Study Context
{study_context}

## Aggregate Statistics
- Total subjects analyzed: {total_subjects}
- High risk postures: {high_risk_count} ({high_risk_count/total_subjects*100:.1f}%)
- Medium risk postures: {medium_risk_count} ({medium_risk_count/total_subjects*100:.1f}%)
- Average neck flexion: {avg_neck_flexion:.1f}°
- Average body symmetry: {avg_symmetry:.1f}/100

## Individual Measurements
{json.dumps(metrics_list, indent=2)}

Generate a research-grade summary including:
1. Population overview
2. Key findings and patterns
3. Statistical significance of findings
4. Implications for workplace design
5. Recommendations for intervention
6. Suggestions for future research

Use appropriate academic language and cite specific measurements.
"""
        
        if self.provider == "anthropic":
            response = self._query_anthropic(prompt)
        else:
            response = self._query_openai(prompt)
        
        return response
