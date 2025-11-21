# Human Factors Platform - Setup Guide

Complete setup instructions for the Human Factors Analysis Platform.

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- CUDA-capable GPU (recommended) or CPU
- SAM 3D Body checkpoint access (see below)

## Step 1: Download SAM 3D Body Checkpoint

First, request access to SAM 3D Body on Hugging Face:
1. Visit https://huggingface.co/facebook/sam-3d-body-dinov3
2. Request access (approval is usually quick)
3. Authenticate with Hugging Face CLI

```bash
# Install huggingface-cli if needed
pip install huggingface-hub

# Login to Hugging Face
huggingface-cli login

# Download the checkpoint
cd sam-3d-body
huggingface-cli download facebook/sam-3d-body-dinov3 --local-dir checkpoints/sam-3d-body-dinov3
```

## Step 2: Backend Setup

```bash
cd human-factors-platform/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install SAM 3D Body dependencies
cd ../../sam-3d-body
pip install -e .

# Return to backend
cd ../human-factors-platform/backend

# Create .env file
cp .env.example .env

# Edit .env and add your API key
# For Anthropic (Claude):
#   ANTHROPIC_API_KEY=sk-ant-...
# For OpenAI (GPT-4):
#   OPENAI_API_KEY=sk-...
```

## Step 3: Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file (optional, defaults to localhost:8000)
cp .env.example .env
```

## Step 4: Get LLM API Key

Choose one of the following LLM providers:

### Option A: NVIDIA NIM (Recommended) 🚀
1. Visit https://build.nvidia.com/
2. Sign up or log in with NVIDIA account
3. Navigate to a model (e.g., Llama 3.1 70B)
4. Click "Get API Key"
5. Add to backend/.env:
   ```bash
   LLM_PROVIDER=nvidia
   NVIDIA_API_KEY=nvapi-...
   NVIDIA_MODEL=meta/llama-3.1-70b-instruct
   ```
6. **Test your setup**: `python test_nvidia.py`

**Benefits**: High performance, streaming, cost-effective  
**See**: [NVIDIA_NIM_SETUP.md](NVIDIA_NIM_SETUP.md) for detailed guide

### Option B: Anthropic Claude
1. Visit https://console.anthropic.com/
2. Create an account
3. Generate an API key
4. Add to backend/.env: 
   ```bash
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### Option C: OpenAI GPT-4
1. Visit https://platform.openai.com/
2. Create an account
3. Generate an API key
4. Add to backend/.env:
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   ```

## Step 5: Run the Application

### Terminal 1 - Backend
```bash
cd human-factors-platform/backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

The backend will start on http://localhost:8000

### Terminal 2 - Frontend
```bash
cd human-factors-platform/frontend
npm run dev
```

The frontend will start on http://localhost:5173

## Step 6: Test the Platform

1. Open http://localhost:5173 in your browser
2. Upload a test image (photo of a person at a desk or workstation)
3. Optionally add context (e.g., "Office worker at desk")
4. Click "Analyze Posture"
5. View the results:
   - 3D pose visualization
   - Ergonomic metrics
   - AI-powered insights

## Troubleshooting

### Backend won't start
- Check that SAM 3D Body checkpoint is downloaded
- Verify Python dependencies are installed
- Check .env file has correct paths

### Frontend won't start
- Run `npm install` again
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

### No LLM insights generated
- Verify API key is set in backend/.env
- Check API key is valid and has credits
- Look at backend console for error messages

### CUDA out of memory
- Reduce image size before uploading
- Use CPU instead (slower): Set `CUDA_VISIBLE_DEVICES=-1` in backend/.env

### Model initialization takes long
- First run downloads model weights (normal)
- Subsequent runs should be faster

## Production Deployment

For production deployment:

1. **Backend**: Deploy to a server with GPU support (AWS EC2 with GPU, GCP, etc.)
2. **Frontend**: Build and deploy to Netlify, Vercel, or similar
3. **Environment**: Set production API keys and URLs
4. **Security**: Add authentication, rate limiting, HTTPS

```bash
# Build frontend for production
cd frontend
npm run build

# The dist/ folder can be deployed to any static hosting
```

## API Documentation

Once the backend is running, visit:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Support

For issues:
1. Check SAM 3D Body repository: https://github.com/facebookresearch/sam-3d-body
2. Review backend logs for detailed error messages
3. Ensure all dependencies are correctly installed
