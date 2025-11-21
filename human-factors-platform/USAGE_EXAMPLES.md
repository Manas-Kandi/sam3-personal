# Usage Examples - Human Factors Analysis Platform

## Example 1: Single Image Analysis

### Web Interface
1. Open http://localhost:5173
2. Upload an image of a person at their workstation
3. Add context: "Office worker at desk using computer"
4. Enable "Generate AI-powered insights"
5. Click "Analyze Posture"

### Expected Output
- **3D Visualization**: Side-by-side comparison of original and reconstructed pose
- **Ergonomic Metrics**: 
  - Neck flexion: 35.2° (Medium Risk)
  - Shoulder asymmetry: 8.3% (Medium Risk)
  - Elbow angles: Left 92°, Right 88° (Optimal)
  - Wrist deviation: 12.5° (Low Risk)
  - Back lean: 28.4° (Medium Risk)
- **AI Insights**: Comprehensive analysis with recommendations

## Example 2: Batch Analysis (API)

```python
import requests

# Upload multiple images for batch analysis
files = [
    ('files', open('worker1.jpg', 'rb')),
    ('files', open('worker2.jpg', 'rb')),
    ('files', open('worker3.jpg', 'rb')),
]

data = {
    'image_context': 'Factory workers at assembly line',
    'generate_summary': True
}

response = requests.post(
    'http://localhost:8000/batch-analyze',
    files=files,
    data=data
)

results = response.json()
print(f"Analyzed {results['successful_analyses']} images")
print(f"Research Summary:\n{results['research_summary']}")
```

## Example 3: Comparative Analysis

Track posture changes over time:

```python
import requests

# Current posture
current_file = open('posture_week4.jpg', 'rb')

# Previous measurements
previous_files = [
    open('posture_week1.jpg', 'rb'),
    open('posture_week2.jpg', 'rb'),
    open('posture_week3.jpg', 'rb'),
]

files = [
    ('current_file', current_file),
    ('previous_files', previous_files[0]),
    ('previous_files', previous_files[1]),
    ('previous_files', previous_files[2]),
]

data = {'time_period': 'over the past 3 weeks'}

response = requests.post(
    'http://localhost:8000/compare-postures',
    files=files,
    data=data
)

comparison = response.json()
print(comparison['comparison']['comparative_analysis'])
```

## Example 4: Research Study Workflow

### Scenario: Ergonomic Assessment of 50 Office Workers

```python
import os
import requests
import pandas as pd

# Directory with participant images
image_dir = 'study_participants/'
results = []

for filename in os.listdir(image_dir):
    if filename.endswith('.jpg'):
        participant_id = filename.split('_')[0]
        
        with open(os.path.join(image_dir, filename), 'rb') as f:
            files = {'file': f}
            data = {
                'image_context': f'Office worker participant {participant_id}',
                'generate_llm_insights': True
            }
            
            response = requests.post(
                'http://localhost:8000/analyze',
                files=files,
                data=data
            )
            
            if response.json()['success']:
                metrics = response.json()['metrics']
                results.append({
                    'participant_id': participant_id,
                    'neck_flexion': metrics['neck_flexion']['angle_degrees'],
                    'shoulder_asymmetry': metrics['shoulder_elevation']['asymmetry_percent'],
                    'back_lean': metrics['back_posture']['forward_lean_degrees'],
                    'risk_level': metrics['risk_assessment']['overall_risk'],
                    'risk_score': metrics['risk_assessment']['risk_score']
                })

# Create DataFrame for analysis
df = pd.DataFrame(results)

# Statistical analysis
print(f"Average neck flexion: {df['neck_flexion'].mean():.1f}°")
print(f"High risk participants: {(df['risk_level'] == 'high').sum()}")
print(f"\nRisk distribution:\n{df['risk_level'].value_counts()}")

# Export for further analysis
df.to_csv('study_results.csv', index=False)
```

## Example 5: Real-Time Monitoring

Monitor a worker's posture throughout the day:

```python
import time
import cv2
import requests
from datetime import datetime

def capture_and_analyze():
    # Capture from webcam
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        # Save temporary image
        temp_file = f'temp_{datetime.now().strftime("%H%M%S")}.jpg'
        cv2.imwrite(temp_file, frame)
        
        # Analyze
        with open(temp_file, 'rb') as f:
            response = requests.post(
                'http://localhost:8000/analyze',
                files={'file': f},
                data={'generate_llm_insights': False}  # Faster without LLM
            )
        
        if response.json()['success']:
            metrics = response.json()['metrics']
            risk = metrics['risk_assessment']['overall_risk']
            
            # Alert if high risk
            if risk == 'high':
                print(f"⚠️ HIGH RISK POSTURE DETECTED at {datetime.now()}")
                print(f"Risk factors: {metrics['risk_assessment']['risk_factors']}")
        
        os.remove(temp_file)

# Monitor every 30 minutes
while True:
    capture_and_analyze()
    time.sleep(1800)  # 30 minutes
```

## Example 6: Integration with Existing Tools

Export data for use in ergonomic assessment software:

```python
import requests
import json

def analyze_and_export(image_path, output_format='json'):
    with open(image_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/analyze',
            files={'file': f},
            data={'generate_llm_insights': True}
        )
    
    results = response.json()
    
    if output_format == 'json':
        # Export as JSON for other tools
        with open('ergonomic_assessment.json', 'w') as f:
            json.dump(results, f, indent=2)
    
    elif output_format == 'csv':
        # Flatten metrics for spreadsheet
        import csv
        metrics = results['metrics']
        
        with open('ergonomic_assessment.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value', 'Unit', 'Risk Level'])
            writer.writerow(['Neck Flexion', 
                           metrics['neck_flexion']['angle_degrees'], 
                           'degrees',
                           metrics['neck_flexion']['risk_level']])
            # ... add more metrics
    
    elif output_format == 'pdf':
        # Generate PDF report (requires reportlab)
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas('ergonomic_report.pdf', pagesize=letter)
        c.drawString(100, 750, "Ergonomic Assessment Report")
        c.drawString(100, 730, f"Risk Level: {results['metrics']['risk_assessment']['overall_risk']}")
        # ... add more content
        c.save()

# Usage
analyze_and_export('worker_photo.jpg', output_format='json')
```

## Example 7: Custom Metrics Extraction

Extract specific measurements for your research:

```python
import requests

def get_custom_measurements(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/analyze',
            files={'file': f}
        )
    
    metrics = response.json()['metrics']
    
    # Extract specific measurements needed for your study
    custom_data = {
        'anthropometric': {
            'shoulder_breadth': metrics['measurements']['shoulder_breadth_cm'],
            'torso_height': metrics['measurements']['torso_height_cm'],
            'arm_length': metrics['measurements']['arm_length_cm']
        },
        'posture_angles': {
            'neck': metrics['neck_flexion']['angle_degrees'],
            'back': metrics['back_posture']['forward_lean_degrees'],
            'left_elbow': metrics['elbow_angles']['left_angle'],
            'right_elbow': metrics['elbow_angles']['right_angle']
        },
        'symmetry': {
            'overall': metrics['body_symmetry']['symmetry_score'],
            'shoulder': metrics['body_symmetry']['shoulder_symmetry'],
            'hip': metrics['body_symmetry']['hip_symmetry']
        }
    }
    
    return custom_data

# Use in your analysis
measurements = get_custom_measurements('participant.jpg')
print(f"Shoulder breadth: {measurements['anthropometric']['shoulder_breadth']:.1f} cm")
```

## Tips for Best Results

1. **Image Quality**: Use well-lit, clear images with the full body visible
2. **Camera Angle**: Side or front-facing views work best
3. **Context**: Provide specific context for more relevant LLM insights
4. **Batch Processing**: Use batch API for large studies to save time
5. **Validation**: Cross-validate critical measurements with manual assessment
6. **Privacy**: Ensure participant consent and data protection compliance
