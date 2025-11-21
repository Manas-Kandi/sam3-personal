# Copyright (c) 2025 Human Factors Platform
"""
FastAPI Backend for Human Factors Analysis Platform
Integrates SAM 3D Body with ergonomic analysis and LLM insights
"""

import sys
import os
from pathlib import Path

# Force CPU mode if CUDA is not available (must be before torch import)
os.environ['CUDA_VISIBLE_DEVICES'] = '' if not os.path.exists('/dev/nvidia0') else os.environ.get('CUDA_VISIBLE_DEVICES', '0')

# Add SAM 3D Body to path
sam3d_path = Path(__file__).parent.parent.parent / "sam-3d-body"
sys.path.insert(0, str(sam3d_path))

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import cv2
import numpy as np
import torch
import base64
from io import BytesIO
from PIL import Image
import json
import traceback

from sam_3d_body import load_sam_3d_body, SAM3DBodyEstimator
from ergonomic_analyzer import ErgonomicAnalyzer
from llm_analyzer import LLMErgonomicAnalyzer

# Try to import visualization, but continue without it if OpenGL is not available
try:
    from tools.vis_utils import visualize_sample_together
    VISUALIZATION_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"⚠️  Warning: Visualization not available (OpenGL/EGL issue): {e}")
    print("ℹ️  Continuing without 3D visualization. Metrics and LLM insights will still work.")
    VISUALIZATION_AVAILABLE = False
    visualize_sample_together = None


app = FastAPI(
    title="Human Factors Analysis Platform",
    description="AI-powered ergonomic analysis using SAM 3D Body + LLM",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for models
class ModelState:
    def __init__(self):
        self.sam3d_estimator = None
        self.ergonomic_analyzer = None
        self.llm_analyzer = None
        self.initialized = False

model_state = ModelState()


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    print("Initializing SAM 3D Body and analysis models...")
    
    try:
        # Initialize SAM 3D Body
        checkpoint_path = os.getenv(
            "SAM3D_CHECKPOINT_PATH",
            str(sam3d_path / "checkpoints/sam-3d-body-dinov3/model.ckpt")
        )
        mhr_path = os.getenv(
            "SAM3D_MHR_PATH",
            str(sam3d_path / "checkpoints/sam-3d-body-dinov3/assets/mhr_model.pt")
        )
        
        # Force CPU on macOS or when CUDA is not available
        if torch.cuda.is_available():
            device = torch.device("cuda")
            print(f"Using device: {device}")
        else:
            device = torch.device("cpu")
            print(f"Using device: {device} (CUDA not available)")
            # Ensure PyTorch uses CPU
            torch.set_default_device('cpu')
        
        # Load SAM 3D Body model
        model, model_cfg = load_sam_3d_body(checkpoint_path, device=device, mhr_path=mhr_path)
        model = model.to(device)  # Ensure model is on correct device
        
        # Create estimator
        model_state.sam3d_estimator = SAM3DBodyEstimator(
            sam_3d_body_model=model,
            model_cfg=model_cfg,
        )
        
        # Store device for later use
        model_state.device = device
        
        # Initialize analyzers
        model_state.ergonomic_analyzer = ErgonomicAnalyzer()
        
        # Initialize LLM (will use environment variables for API keys)
        llm_provider = os.getenv("LLM_PROVIDER", "anthropic")
        model_state.llm_analyzer = LLMErgonomicAnalyzer(provider=llm_provider)
        
        model_state.initialized = True
        print("✓ Models initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing models: {e}")
        traceback.print_exc()
        print("\nNote: Make sure to:")
        print("1. Download SAM 3D Body checkpoint")
        print("2. Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable")
        print("3. Ensure sam-3d-body is in the correct path")


class AnalysisRequest(BaseModel):
    """Request model for analysis."""
    image_context: Optional[str] = ""
    generate_llm_insights: bool = True


class AnalysisResponse(BaseModel):
    """Response model for analysis."""
    success: bool
    message: str
    metrics: Optional[dict] = None
    llm_insights: Optional[dict] = None
    visualization: Optional[str] = None  # Base64 encoded image
    num_people: int = 0


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "initialized": model_state.initialized,
        "message": "Human Factors Analysis Platform API"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy" if model_state.initialized else "initializing",
        "sam3d_loaded": model_state.sam3d_estimator is not None,
        "ergonomic_analyzer_loaded": model_state.ergonomic_analyzer is not None,
        "llm_analyzer_loaded": model_state.llm_analyzer is not None,
        "device": str(next(model_state.sam3d_estimator.model.parameters()).device) if model_state.sam3d_estimator else "unknown"
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    image_context: str = Form(""),
    generate_llm_insights: bool = Form(True)
):
    """
    Analyze uploaded image for ergonomic assessment.
    
    Args:
        file: Uploaded image file
        image_context: Optional context about the image
        generate_llm_insights: Whether to generate LLM insights
    
    Returns:
        Analysis results with metrics, insights, and visualization
    """
    
    if not model_state.initialized:
        raise HTTPException(status_code=503, detail="Models not initialized yet")
    
    try:
        # Read and decode image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img_bgr is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        
        # Process with SAM 3D Body
        print("Processing image with SAM 3D Body...")
        outputs = model_state.sam3d_estimator.process_one_image(img_rgb)
        
        if not outputs or len(outputs) == 0:
            return AnalysisResponse(
                success=False,
                message="No people detected in the image",
                num_people=0
            )
        
        # Analyze first person (can be extended for multi-person)
        person_output = outputs[0]
        
        # Extract ergonomic metrics
        print("Calculating ergonomic metrics...")
        metrics = model_state.ergonomic_analyzer.analyze_posture(person_output)
        
        # Generate LLM insights if requested
        llm_insights = None
        if generate_llm_insights:
            print("Generating LLM insights...")
            try:
                llm_insights = model_state.llm_analyzer.generate_insights(
                    metrics,
                    image_context=image_context
                )
            except Exception as e:
                print(f"Warning: LLM analysis failed: {e}")
                llm_insights = {"error": str(e)}
        
        # Generate visualization (if available)
        vis_base64 = None
        if VISUALIZATION_AVAILABLE:
            print("Creating visualization...")
            try:
                vis_img = visualize_sample_together(img_bgr, outputs, model_state.sam3d_estimator.faces)
                # Convert visualization to base64
                _, buffer = cv2.imencode('.jpg', vis_img)
                vis_base64 = base64.b64encode(buffer).decode('utf-8')
            except Exception as e:
                print(f"Warning: Visualization failed: {e}")
                # Use original image as fallback
                _, buffer = cv2.imencode('.jpg', img_bgr)
                vis_base64 = base64.b64encode(buffer).decode('utf-8')
        else:
            # Use original image when visualization is not available
            print("Visualization not available, using original image...")
            _, buffer = cv2.imencode('.jpg', img_bgr)
            vis_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return AnalysisResponse(
            success=True,
            message="Analysis completed successfully",
            metrics=metrics,
            llm_insights=llm_insights,
            visualization=vis_base64,
            num_people=len(outputs)
        )
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/batch-analyze")
async def batch_analyze(
    files: List[UploadFile] = File(...),
    image_context: str = Form(""),
    generate_summary: bool = Form(True)
):
    """
    Analyze multiple images and generate aggregate summary.
    
    Args:
        files: List of uploaded image files
        image_context: Context about the study
        generate_summary: Whether to generate research summary
    
    Returns:
        Batch analysis results with individual metrics and summary
    """
    
    if not model_state.initialized:
        raise HTTPException(status_code=503, detail="Models not initialized yet")
    
    results = []
    all_metrics = []
    
    for idx, file in enumerate(files):
        try:
            # Read and process image
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img_bgr is None:
                results.append({"filename": file.filename, "error": "Invalid image"})
                continue
            
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            # Process with SAM 3D Body
            outputs = model_state.sam3d_estimator.process_one_image(img_rgb)
            
            if not outputs:
                results.append({"filename": file.filename, "error": "No people detected"})
                continue
            
            # Analyze first person
            person_output = outputs[0]
            metrics = model_state.ergonomic_analyzer.analyze_posture(person_output)
            
            all_metrics.append(metrics)
            results.append({
                "filename": file.filename,
                "metrics": metrics,
                "num_people": len(outputs)
            })
            
        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})
    
    # Generate research summary if requested
    summary = None
    if generate_summary and all_metrics:
        try:
            summary = model_state.llm_analyzer.generate_research_summary(
                all_metrics,
                study_context=image_context
            )
        except Exception as e:
            summary = f"Summary generation failed: {str(e)}"
    
    return {
        "success": True,
        "total_images": len(files),
        "successful_analyses": len(all_metrics),
        "results": results,
        "research_summary": summary
    }


@app.post("/compare-postures")
async def compare_postures(
    current_file: UploadFile = File(...),
    previous_files: List[UploadFile] = File(...),
    time_period: str = Form("over the past week")
):
    """
    Compare current posture with previous measurements.
    
    Args:
        current_file: Current image
        previous_files: Previous measurement images
        time_period: Description of time period
    
    Returns:
        Comparative analysis
    """
    
    if not model_state.initialized:
        raise HTTPException(status_code=503, detail="Models not initialized yet")
    
    try:
        # Process current image
        contents = await current_file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        
        outputs = model_state.sam3d_estimator.process_one_image(img_rgb)
        if not outputs:
            raise HTTPException(status_code=400, detail="No people detected in current image")
        
        current_metrics = model_state.ergonomic_analyzer.analyze_posture(outputs[0])
        
        # Process previous images
        previous_metrics = []
        for prev_file in previous_files:
            contents = await prev_file.read()
            nparr = np.frombuffer(contents, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            outputs = model_state.sam3d_estimator.process_one_image(img_rgb)
            if outputs:
                metrics = model_state.ergonomic_analyzer.analyze_posture(outputs[0])
                previous_metrics.append(metrics)
        
        # Generate comparative analysis
        comparison = model_state.llm_analyzer.generate_comparative_analysis(
            current_metrics,
            previous_metrics,
            time_period=time_period
        )
        
        return {
            "success": True,
            "current_metrics": current_metrics,
            "previous_count": len(previous_metrics),
            "comparison": comparison
        }
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
