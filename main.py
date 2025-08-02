from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import shutil
import logging
from typing import Optional
import asyncio
import subprocess
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="iAvatar SadTalker API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables with defaults
SADTALKER_PATH = os.getenv("SADTALKER_PATH", "/workspace/SadTalker")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/workspace/iAvatar/outputs")
TEMP_DIR = os.getenv("TEMP_DIR", "/workspace/iAvatar/temp")

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

class SadTalkerGenerator:
    def __init__(self):
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize SadTalker models"""
        if self.is_initialized:
            return
            
        try:
            # Check if SadTalker is available
            if not os.path.exists(SADTALKER_PATH):
                raise Exception("SadTalker not found. Please install SadTalker first.")
                
            # Download checkpoints if needed
            await self._download_checkpoints()
            self.is_initialized = True
            logger.info("SadTalker initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SadTalker: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")
    
    async def _download_checkpoints(self):
        """Download required model checkpoints"""
        checkpoint_script = os.path.join(SADTALKER_PATH, "scripts", "download_models.sh")
        if os.path.exists(checkpoint_script):
            try:
                result = subprocess.run(
                    ["bash", checkpoint_script], 
                    cwd=SADTALKER_PATH,
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
                if result.returncode != 0:
                    logger.warning(f"Checkpoint download warning: {result.stderr}")
            except subprocess.TimeoutExpired:
                logger.warning("Checkpoint download timeout - continuing anyway")
    
    async def generate_video(
        self, 
        image_path: str, 
        audio_path: str, 
        output_path: str,
        preprocess: str = "crop",
        still: bool = False,
        use_enhancer: bool = False
    ) -> str:
        """Generate talking head video using SadTalker"""
        try:
            cmd = [
                "python", "inference.py",
                "--driven_audio", audio_path,
                "--source_image", image_path,
                "--result_dir", os.path.dirname(output_path),
                "--preprocess", preprocess
            ]
            
            # Add CPU flag only if no GPU available
            if not self._has_gpu():
                cmd.append("--cpu")
            
            if still:
                cmd.append("--still")
            if use_enhancer:
                cmd.append("--enhancer", "gfpgan")
                
            logger.info(f"Running SadTalker command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=SADTALKER_PATH,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                logger.error(f"SadTalker error: {result.stderr}")
                raise Exception(f"SadTalker generation failed: {result.stderr}")
                
            # Find the generated video file
            result_files = list(Path(os.path.dirname(output_path)).glob("*.mp4"))
            if not result_files:
                raise Exception("No output video generated")
                
            # Move to desired output path
            shutil.move(str(result_files[0]), output_path)
            return output_path
            
        except subprocess.TimeoutExpired:
            raise Exception("Video generation timeout")
        except Exception as e:
            logger.error(f"Video generation error: {str(e)}")
            raise Exception(f"Generation failed: {str(e)}")
    
    def _has_gpu(self) -> bool:
        """Check if GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False

# Initialize generator
generator = SadTalkerGenerator()

@app.on_event("startup")
async def startup_event():
    """Initialize SadTalker on startup"""
    await generator.initialize()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "iAvatar SadTalker API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "sadtalker_initialized": generator.is_initialized,
        "gpu_available": generator._has_gpu() if generator.is_initialized else False
    }

@app.post("/generate-avatar")
async def generate_avatar(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    preprocess: str = "crop",
    still: bool = False,
    use_enhancer: bool = False
):
    """Generate talking head video from image and audio"""
    
    if not generator.is_initialized:
        raise HTTPException(status_code=503, detail="SadTalker not initialized")
    
    # Validate file types
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file")
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio file")
    
    # Generate unique filename
    import uuid
    job_id = str(uuid.uuid4())
    
    try:
        # Save uploaded files
        image_path = f"{TEMP_DIR}/{job_id}_image.jpg"
        audio_path = f"{TEMP_DIR}/{job_id}_audio.wav"
        output_path = f"{OUTPUT_DIR}/{job_id}_result.mp4"
        
        # Save image
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Save audio
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # Generate video
        result_path = await generator.generate_video(
            image_path=image_path,
            audio_path=audio_path,
            output_path=output_path,
            preprocess=preprocess,
            still=still,
            use_enhancer=use_enhancer
        )
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_files, image_path, audio_path)
        
        return FileResponse(
            result_path,
            media_type="video/mp4",
            filename=f"avatar_{job_id}.mp4"
        )
        
    except Exception as e:
        # Cleanup on error
        for path in [image_path, audio_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-avatar-async")
async def generate_avatar_async(
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    preprocess: str = "crop",
    still: bool = False,
    use_enhancer: bool = False
):
    """Start avatar generation job and return job ID"""
    
    if not generator.is_initialized:
        raise HTTPException(status_code=503, detail="SadTalker not initialized")
    
    import uuid
    job_id = str(uuid.uuid4())
    
    # Save files and start background task
    image_path = f"{TEMP_DIR}/{job_id}_image.jpg"
    audio_path = f"{TEMP_DIR}/{job_id}_audio.wav"
    
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
    
    # Start background generation
    asyncio.create_task(
        background_generate(job_id, image_path, audio_path, preprocess, still, use_enhancer)
    )
    
    return {"job_id": job_id, "status": "processing"}

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and download result if ready"""
    output_path = f"{OUTPUT_DIR}/{job_id}_result.mp4"
    
    if os.path.exists(output_path):
        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename=f"avatar_{job_id}.mp4"
        )
    else:
        return {"job_id": job_id, "status": "processing"}

async def background_generate(job_id: str, image_path: str, audio_path: str, preprocess: str, still: bool, use_enhancer: bool):
    """Background task for video generation"""
    try:
        output_path = f"{OUTPUT_DIR}/{job_id}_result.mp4"
        await generator.generate_video(
            image_path=image_path,
            audio_path=audio_path,
            output_path=output_path,
            preprocess=preprocess,
            still=still,
            use_enhancer=use_enhancer
        )
    except Exception as e:
        logger.error(f"Background generation failed for {job_id}: {str(e)}")
    finally:
        # Cleanup temp files
        cleanup_temp_files(image_path, audio_path)

def cleanup_temp_files(*file_paths):
    """Clean up temporary files"""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.warning(f"Failed to cleanup {path}: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)