# Human Factors Analysis Platform

An intelligent platform for Human Factors researchers that combines SAM 3D Body with LLM-powered ergonomic analysis.

## Features

- **Image Upload & Processing**: Upload workplace photos for instant analysis
- **3D Pose Reconstruction**: SAM 3D Body generates accurate 3D human meshes
- **Ergonomic Metrics**: Automatic calculation of key ergonomic measurements
- **AI-Powered Insights**: LLM generates comprehensive ergonomic assessments based on actual metrics
- **Multiple LLM Providers**: Support for Anthropic Claude, OpenAI GPT-4, and **NVIDIA NIM** (Llama 3.1)
- **Visual Reports**: Side-by-side comparison of original image and 3D reconstruction

## Architecture

```
Frontend (React + TailwindCSS)
    ↓
Backend API (FastAPI)
    ↓
SAM 3D Body Model → Ergonomic Metrics Calculator → LLM Analyzer
    ↓
Results with visualizations + AI insights
```

## Installation

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Download SAM 3D Body checkpoint
hf download facebook/sam-3d-body-dinov3 --local-dir checkpoints/sam-3d-body-dinov3
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Usage

### Start Backend
```bash
cd backend
python app.py
```

### Start Frontend
```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173` to use the platform.

## LLM Provider Options

The platform supports three LLM providers for generating ergonomic insights:

### 1. **NVIDIA NIM** (Recommended) 🚀
- **Models**: Llama 3.1 (8B, 70B, 405B), Mistral, and more
- **Benefits**: High performance, streaming support, cost-effective
- **Setup**: See [NVIDIA_NIM_SETUP.md](NVIDIA_NIM_SETUP.md) for detailed instructions
- **Get API Key**: https://build.nvidia.com/

```bash
# In backend/.env
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-YOUR_KEY_HERE
NVIDIA_MODEL=meta/llama-3.1-70b-instruct
```

### 2. **Anthropic Claude**
- **Model**: Claude 3.5 Sonnet
- **Benefits**: Excellent reasoning, detailed analysis
- **Get API Key**: https://console.anthropic.com/

```bash
# In backend/.env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
```

### 3. **OpenAI GPT-4**
- **Model**: GPT-4o
- **Benefits**: Well-established, reliable
- **Get API Key**: https://platform.openai.com/

```bash
# In backend/.env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-YOUR_KEY_HERE
```

## Key Components

- **Ergonomic Metrics Calculator**: Extracts neck angle, shoulder elevation, elbow angle, wrist position, back posture
- **LLM Integration**: Uses NVIDIA/OpenAI/Anthropic API to generate insights from metrics
- **Visualization**: 3D mesh overlay, keypoint visualization, metric dashboards

## Research Applications

- Workplace ergonomic assessments
- Product design validation
- Anthropometric studies
- Posture analysis
- Injury risk assessment
