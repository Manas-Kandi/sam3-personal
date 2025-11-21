# Copyright (c) 2025 Human Factors Platform
"""
Ergonomic Metrics Calculator
Extracts key ergonomic measurements from SAM 3D Body outputs
"""

import numpy as np
from typing import Dict, List, Any
import torch


class ErgonomicAnalyzer:
    """
    Analyzes 3D pose data to extract ergonomic metrics for Human Factors research.
    """
    
    # MHR70 keypoint indices
    KEYPOINTS = {
        'nose': 0,
        'left_eye': 1,
        'right_eye': 2,
        'left_ear': 3,
        'right_ear': 4,
        'left_shoulder': 5,
        'right_shoulder': 6,
        'left_elbow': 7,
        'right_elbow': 8,
        'left_hip': 9,
        'right_hip': 10,
        'left_knee': 11,
        'right_knee': 12,
        'left_ankle': 13,
        'right_ankle': 14,
        'left_wrist': 41,
        'right_wrist': 62,
    }
    
    def __init__(self):
        """Initialize the ergonomic analyzer."""
        self.risk_thresholds = {
            'neck_flexion': {'low': 20, 'medium': 45, 'high': 60},
            'shoulder_elevation': {'low': 20, 'medium': 45, 'high': 60},
            'elbow_angle': {'optimal_min': 70, 'optimal_max': 110},
            'wrist_extension': {'low': 15, 'medium': 30, 'high': 45},
            'back_angle': {'low': 20, 'medium': 45, 'high': 60},
        }
    
    def analyze_posture(self, sam3d_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze posture from SAM 3D Body output.
        
        Args:
            sam3d_output: Dictionary containing SAM 3D Body predictions
                - 'vertices': 3D mesh vertices (N, 3)
                - 'joints_3d': 3D joint positions (70, 3)
                - 'camera': Camera parameters
        
        Returns:
            Dictionary with ergonomic metrics and risk assessments
        """
        joints_3d = sam3d_output.get('joints_3d')
        
        if joints_3d is None:
            raise ValueError("No 3D joints found in SAM 3D Body output")
        
        # Convert to numpy if tensor
        if torch.is_tensor(joints_3d):
            joints_3d = joints_3d.cpu().numpy()
        
        metrics = {}
        
        # Calculate all ergonomic metrics
        metrics['neck_flexion'] = self._calculate_neck_flexion(joints_3d)
        metrics['shoulder_elevation'] = self._calculate_shoulder_elevation(joints_3d)
        metrics['elbow_angles'] = self._calculate_elbow_angles(joints_3d)
        metrics['wrist_extension'] = self._calculate_wrist_extension(joints_3d)
        metrics['back_posture'] = self._calculate_back_posture(joints_3d)
        metrics['body_symmetry'] = self._calculate_body_symmetry(joints_3d)
        
        # Calculate anthropometric measurements
        metrics['measurements'] = self._calculate_measurements(joints_3d)
        
        # Assess overall risk
        metrics['risk_assessment'] = self._assess_risk(metrics)
        
        return metrics
    
    def _calculate_neck_flexion(self, joints: np.ndarray) -> Dict[str, float]:
        """Calculate neck flexion angle (forward head posture)."""
        nose = joints[self.KEYPOINTS['nose']]
        left_shoulder = joints[self.KEYPOINTS['left_shoulder']]
        right_shoulder = joints[self.KEYPOINTS['right_shoulder']]
        
        # Midpoint of shoulders
        shoulder_mid = (left_shoulder + right_shoulder) / 2
        
        # Vector from shoulder to nose
        neck_vector = nose - shoulder_mid
        
        # Vertical reference (assuming y-axis is up)
        vertical = np.array([0, 1, 0])
        
        # Calculate angle
        angle = self._angle_between_vectors(neck_vector, vertical)
        
        # Forward flexion is deviation from vertical
        flexion_angle = abs(90 - angle)
        
        return {
            'angle_degrees': float(flexion_angle),
            'risk_level': self._get_risk_level(flexion_angle, 'neck_flexion'),
            'description': 'Forward head posture angle'
        }
    
    def _calculate_shoulder_elevation(self, joints: np.ndarray) -> Dict[str, float]:
        """Calculate shoulder elevation and asymmetry."""
        left_shoulder = joints[self.KEYPOINTS['left_shoulder']]
        right_shoulder = joints[self.KEYPOINTS['right_shoulder']]
        left_hip = joints[self.KEYPOINTS['left_hip']]
        right_hip = joints[self.KEYPOINTS['right_hip']]
        
        # Calculate shoulder height relative to hips
        hip_mid = (left_hip + right_hip) / 2
        shoulder_mid = (left_shoulder + right_shoulder) / 2
        
        # Shoulder asymmetry
        shoulder_height_diff = abs(left_shoulder[1] - right_shoulder[1])
        torso_height = abs(shoulder_mid[1] - hip_mid[1])
        
        asymmetry_percent = (shoulder_height_diff / torso_height) * 100 if torso_height > 0 else 0
        
        return {
            'asymmetry_percent': float(asymmetry_percent),
            'left_height': float(left_shoulder[1]),
            'right_height': float(right_shoulder[1]),
            'risk_level': 'high' if asymmetry_percent > 10 else 'medium' if asymmetry_percent > 5 else 'low',
            'description': 'Shoulder elevation asymmetry'
        }
    
    def _calculate_elbow_angles(self, joints: np.ndarray) -> Dict[str, Any]:
        """Calculate elbow angles for both arms."""
        left_elbow_angle = self._calculate_joint_angle(
            joints[self.KEYPOINTS['left_shoulder']],
            joints[self.KEYPOINTS['left_elbow']],
            joints[self.KEYPOINTS['left_wrist']]
        )
        
        right_elbow_angle = self._calculate_joint_angle(
            joints[self.KEYPOINTS['right_shoulder']],
            joints[self.KEYPOINTS['right_elbow']],
            joints[self.KEYPOINTS['right_wrist']]
        )
        
        optimal_min = self.risk_thresholds['elbow_angle']['optimal_min']
        optimal_max = self.risk_thresholds['elbow_angle']['optimal_max']
        
        return {
            'left_angle': float(left_elbow_angle),
            'right_angle': float(right_elbow_angle),
            'left_optimal': optimal_min <= left_elbow_angle <= optimal_max,
            'right_optimal': optimal_min <= right_elbow_angle <= optimal_max,
            'description': 'Elbow flexion angles (optimal: 70-110°)'
        }
    
    def _calculate_wrist_extension(self, joints: np.ndarray) -> Dict[str, float]:
        """Calculate wrist extension/flexion angles."""
        # Simplified wrist angle calculation
        # In full implementation, would use hand keypoints for precise measurement
        left_elbow = joints[self.KEYPOINTS['left_elbow']]
        left_wrist = joints[self.KEYPOINTS['left_wrist']]
        
        right_elbow = joints[self.KEYPOINTS['right_elbow']]
        right_wrist = joints[self.KEYPOINTS['right_wrist']]
        
        # Estimate wrist deviation from forearm alignment
        left_forearm = left_wrist - left_elbow
        right_forearm = right_wrist - right_elbow
        
        # Simplified deviation estimate
        left_deviation = abs(np.arctan2(left_forearm[2], left_forearm[0])) * 180 / np.pi
        right_deviation = abs(np.arctan2(right_forearm[2], right_forearm[0])) * 180 / np.pi
        
        avg_deviation = (left_deviation + right_deviation) / 2
        
        return {
            'left_deviation': float(left_deviation),
            'right_deviation': float(right_deviation),
            'average_deviation': float(avg_deviation),
            'risk_level': self._get_risk_level(avg_deviation, 'wrist_extension'),
            'description': 'Wrist extension/deviation angle'
        }
    
    def _calculate_back_posture(self, joints: np.ndarray) -> Dict[str, float]:
        """Calculate back/spine angle."""
        left_shoulder = joints[self.KEYPOINTS['left_shoulder']]
        right_shoulder = joints[self.KEYPOINTS['right_shoulder']]
        left_hip = joints[self.KEYPOINTS['left_hip']]
        right_hip = joints[self.KEYPOINTS['right_hip']]
        
        shoulder_mid = (left_shoulder + right_shoulder) / 2
        hip_mid = (left_hip + right_hip) / 2
        
        # Spine vector
        spine_vector = shoulder_mid - hip_mid
        
        # Vertical reference
        vertical = np.array([0, 1, 0])
        
        # Calculate angle from vertical
        angle = self._angle_between_vectors(spine_vector, vertical)
        
        # Forward lean is deviation from vertical
        forward_lean = abs(angle)
        
        return {
            'forward_lean_degrees': float(forward_lean),
            'risk_level': self._get_risk_level(forward_lean, 'back_angle'),
            'description': 'Spine forward lean angle'
        }
    
    def _calculate_body_symmetry(self, joints: np.ndarray) -> Dict[str, float]:
        """Calculate overall body symmetry."""
        # Compare left and right side joint positions
        left_shoulder = joints[self.KEYPOINTS['left_shoulder']]
        right_shoulder = joints[self.KEYPOINTS['right_shoulder']]
        left_hip = joints[self.KEYPOINTS['left_hip']]
        right_hip = joints[self.KEYPOINTS['right_hip']]
        
        # Calculate midline
        shoulder_mid = (left_shoulder + right_shoulder) / 2
        hip_mid = (left_hip + right_hip) / 2
        
        # Symmetry score (0-100, higher is more symmetric)
        shoulder_symmetry = 100 - min(100, abs(left_shoulder[1] - right_shoulder[1]) * 100)
        hip_symmetry = 100 - min(100, abs(left_hip[1] - right_hip[1]) * 100)
        
        overall_symmetry = (shoulder_symmetry + hip_symmetry) / 2
        
        return {
            'symmetry_score': float(overall_symmetry),
            'shoulder_symmetry': float(shoulder_symmetry),
            'hip_symmetry': float(hip_symmetry),
            'description': 'Overall body symmetry (0-100)'
        }
    
    def _calculate_measurements(self, joints: np.ndarray) -> Dict[str, float]:
        """Calculate anthropometric measurements."""
        # Shoulder breadth
        left_shoulder = joints[self.KEYPOINTS['left_shoulder']]
        right_shoulder = joints[self.KEYPOINTS['right_shoulder']]
        shoulder_breadth = np.linalg.norm(right_shoulder - left_shoulder)
        
        # Torso height
        shoulder_mid = (left_shoulder + right_shoulder) / 2
        left_hip = joints[self.KEYPOINTS['left_hip']]
        right_hip = joints[self.KEYPOINTS['right_hip']]
        hip_mid = (left_hip + right_hip) / 2
        torso_height = np.linalg.norm(shoulder_mid - hip_mid)
        
        # Arm length (shoulder to wrist)
        left_wrist = joints[self.KEYPOINTS['left_wrist']]
        left_arm_length = (
            np.linalg.norm(joints[self.KEYPOINTS['left_elbow']] - left_shoulder) +
            np.linalg.norm(left_wrist - joints[self.KEYPOINTS['left_elbow']])
        )
        
        # Leg length (hip to ankle)
        left_ankle = joints[self.KEYPOINTS['left_ankle']]
        left_leg_length = (
            np.linalg.norm(joints[self.KEYPOINTS['left_knee']] - left_hip) +
            np.linalg.norm(left_ankle - joints[self.KEYPOINTS['left_knee']])
        )
        
        return {
            'shoulder_breadth_cm': float(shoulder_breadth * 100),  # Convert to cm
            'torso_height_cm': float(torso_height * 100),
            'arm_length_cm': float(left_arm_length * 100),
            'leg_length_cm': float(left_leg_length * 100),
        }
    
    def _assess_risk(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall ergonomic risk based on all metrics."""
        risk_scores = []
        risk_factors = []
        
        # Neck flexion risk
        neck_risk = metrics['neck_flexion']['risk_level']
        if neck_risk in ['medium', 'high']:
            risk_factors.append(f"Neck flexion: {metrics['neck_flexion']['angle_degrees']:.1f}°")
            risk_scores.append(2 if neck_risk == 'medium' else 3)
        
        # Shoulder elevation risk
        shoulder_risk = metrics['shoulder_elevation']['risk_level']
        if shoulder_risk in ['medium', 'high']:
            risk_factors.append(f"Shoulder asymmetry: {metrics['shoulder_elevation']['asymmetry_percent']:.1f}%")
            risk_scores.append(2 if shoulder_risk == 'medium' else 3)
        
        # Elbow angle risk
        if not metrics['elbow_angles']['left_optimal'] or not metrics['elbow_angles']['right_optimal']:
            risk_factors.append("Elbow angles outside optimal range")
            risk_scores.append(2)
        
        # Wrist extension risk
        wrist_risk = metrics['wrist_extension']['risk_level']
        if wrist_risk in ['medium', 'high']:
            risk_factors.append(f"Wrist deviation: {metrics['wrist_extension']['average_deviation']:.1f}°")
            risk_scores.append(2 if wrist_risk == 'medium' else 3)
        
        # Back posture risk
        back_risk = metrics['back_posture']['risk_level']
        if back_risk in ['medium', 'high']:
            risk_factors.append(f"Forward lean: {metrics['back_posture']['forward_lean_degrees']:.1f}°")
            risk_scores.append(2 if back_risk == 'medium' else 3)
        
        # Calculate overall risk score
        overall_score = sum(risk_scores) / max(len(risk_scores), 1) if risk_scores else 0
        
        if overall_score >= 2.5:
            overall_risk = 'high'
        elif overall_score >= 1.5:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        return {
            'overall_risk': overall_risk,
            'risk_score': float(overall_score),
            'risk_factors': risk_factors,
            'recommendations': self._generate_recommendations(risk_factors)
        }
    
    def _generate_recommendations(self, risk_factors: List[str]) -> List[str]:
        """Generate ergonomic recommendations based on risk factors."""
        recommendations = []
        
        for factor in risk_factors:
            if 'Neck' in factor:
                recommendations.append("Adjust monitor height to eye level to reduce neck strain")
            if 'Shoulder' in factor:
                recommendations.append("Ensure shoulders are relaxed and level; adjust chair armrests")
            if 'Elbow' in factor:
                recommendations.append("Position keyboard/mouse to maintain 90° elbow angle")
            if 'Wrist' in factor:
                recommendations.append("Use wrist rest and maintain neutral wrist position")
            if 'Forward lean' in factor or 'lean' in factor:
                recommendations.append("Adjust chair back support; sit upright with lumbar support")
        
        if not recommendations:
            recommendations.append("Posture appears ergonomically sound; maintain current setup")
        
        return recommendations
    
    def _angle_between_vectors(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate angle between two vectors in degrees."""
        v1_norm = v1 / (np.linalg.norm(v1) + 1e-8)
        v2_norm = v2 / (np.linalg.norm(v2) + 1e-8)
        cos_angle = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
        angle_rad = np.arccos(cos_angle)
        return float(np.degrees(angle_rad))
    
    def _calculate_joint_angle(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Calculate angle at joint p2 formed by points p1-p2-p3."""
        v1 = p1 - p2
        v2 = p3 - p2
        return self._angle_between_vectors(v1, v2)
    
    def _get_risk_level(self, value: float, metric_type: str) -> str:
        """Determine risk level based on threshold values."""
        thresholds = self.risk_thresholds.get(metric_type, {})
        
        if value < thresholds.get('low', float('inf')):
            return 'low'
        elif value < thresholds.get('medium', float('inf')):
            return 'medium'
        else:
            return 'high'
