# RunPod Setup Guide for iAvatar SadTalker API

Complete guide to deploy and test the SadTalker API on RunPod GPU instances.

## 📋 Prerequisites

- RunPod account with billing setup
- SSH client (Terminal on Mac/Linux, PuTTY on Windows)
- Basic command line knowledge

## 🚀 Step 1: Deploy RunPod Instance

### Pod Configuration
1. **GPU**: RTX 4090 (24GB VRAM) or RTX 3090 (24GB VRAM)
2. **Template**: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`
3. **Container Disk**: 50GB+
4. **Network Volume**: 20GB (recommended for model persistence)
5. **Ports**: 
   - `8000` (HTTP for API)
   - `22` (SSH)

### Pricing Options
- **Spot**: $0.20-0.40/hour (can be terminated)
- **On-Demand**: $0.79/hour (guaranteed)

## 🔌 Step 2: SSH Connection

### Get Connection Details
1. Go to RunPod dashboard → My Pods
2. Click "Connect" on your running pod
3. Copy SSH command

### Connect via SSH
```bash
# Replace with your actual pod details
ssh root@[POD_IP] -p [POD_PORT]

# Example:
ssh root@173.252.74.22 -p 22476
```

### Verify Environment
```bash
# Quick GPU check
nvidia-smi

# Comprehensive system test (recommended)
cd /workspace/iAvatar
python3 test_gpu.py

# Should show:
# 🎉 All tests passed! Ready for SadTalker.
```

## 📦 Step 3: Install SadTalker

### Clone and Setup SadTalker
```bash
# Navigate to workspace
cd /workspace

# Clone SadTalker repository
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker

# Install dependencies
pip install -r requirements.txt

# Download pretrained models (5-10 minutes)
bash scripts/download_models.sh
```

### Verify Installation
```bash
# Check models downloaded
ls -la checkpoints/
ls -la gfpgan/weights/

# Should see multiple .pth files
```

## 🔧 Step 4: Setup iAvatar API Service

### Clone iAvatar Repository
```bash
cd /workspace
git clone https://github.com/ShuhaoZQGG/iAvatar.git
cd iAvatar
```

### Install API Dependencies
```bash
pip install -r requirements.txt
```

### Create Required Directories
```bash
mkdir -p /workspace/iAvatar/outputs
mkdir -p /workspace/iAvatar/temp
```

### Environment Variables (Optional)
```bash
# Set custom paths if needed
export SADTALKER_PATH="/workspace/SadTalker"
export OUTPUT_DIR="/workspace/iAvatar/outputs"
export TEMP_DIR="/workspace/iAvatar/temp"
```

## 🌐 Step 5: Start API Service

### Start the FastAPI Server
```bash
cd /workspace/iAvatar
python3 main.py
```

### Expected Output
```
INFO:__main__:SadTalker initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Keep Service Running (Optional)
```bash
# Use tmux to persist session
tmux new-session -d -s iavatar
tmux send-keys -t iavatar "cd /workspace/iAvatar && python3 main.py" Enter

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t iavatar
```

## 🧪 Step 6: Test API

### Health Check
```bash
# From another terminal or external machine
curl http://[POD_IP]:8000/health

# Example response:
{
  "status": "healthy",
  "sadtalker_initialized": true,
  "gpu_available": true
}
```

### Generate Test Files and Test API
```bash
cd /workspace/iAvatar

# Run test script (creates sample image and audio)
python3 test_avatar.py

# When prompted, enter your API URL:
# http://[POD_IP]:8000
# or
# http://0.0.0.0:8000 (if testing from same pod)
```

### Manual API Test with curl
```bash
# Create test files first
python3 -c "
from test_avatar import create_test_image, create_test_audio
create_test_image()
create_test_audio()
"

# Test API with curl
curl -X POST "http://[POD_IP]:8000/generate-avatar" \
  -F "image=@test_face.jpg" \
  -F "audio=@test_speech.wav" \
  --output generated_avatar.mp4

# Check generated video
ls -la generated_avatar.mp4
```

## ✅ Step 7: Verify Success

### Check Generated Video
```bash
# Video should be created
ls -la generated_avatar.mp4

# Should be several MB in size
# Download to view: scp root@[POD_IP]:/workspace/iAvatar/generated_avatar.mp4 ./
```

### API Endpoints Available
- `GET /` - Basic health check
- `GET /health` - Detailed status
- `POST /generate-avatar` - Synchronous video generation
- `POST /generate-avatar-async` - Asynchronous generation
- `GET /job/{job_id}` - Check async job status

## 🔄 Persistence & Recovery

### Network Volume Benefits
- SadTalker models (~10GB) persist between pod restarts
- Faster setup on new instances

### Quick Recovery (if pod terminated)
```bash
# 1. Deploy new pod with same network volume
# 2. SSH into new pod
cd /workspace

# 3. Clone iAvatar code (container disk is wiped)
git clone https://github.com/ShuhaoZQGG/iAvatar.git
cd iAvatar
pip install -r requirements.txt

# 4. Verify environment
python3 test_gpu.py

# 5. SadTalker should still exist from network volume
ls -la /workspace/SadTalker

# 6. Start service
python3 main.py
```

## 🔧 Troubleshooting

### Comprehensive Diagnostics
```bash
# Run full system test
cd /workspace/iAvatar
python3 test_gpu.py

# This will check:
# - NVIDIA drivers and GPU detection
# - PyTorch CUDA availability  
# - All required ML libraries
# - System information
```

### GPU Not Available
```bash
# Check NVIDIA drivers
nvidia-smi

# If nvidia-smi fails:
# - Pod may not have GPU allocated
# - Try different GPU type or region
# - Switch to on-demand if spot unavailable
```

### SadTalker Models Missing
```bash
cd /workspace/SadTalker
bash scripts/download_models.sh
```

### Port Access Issues
- Ensure port 8000 is exposed in RunPod settings
- Use pod's public IP for external access
- Check firewall settings

### Memory Issues
- RTX 4090: 24GB VRAM should be sufficient
- Monitor usage: `nvidia-smi`
- Reduce batch size if needed

### Library Issues
```bash
# If test_gpu.py shows missing libraries:
pip install -r requirements.txt

# For specific library errors:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### API Errors
```bash
# Test environment first
python3 test_gpu.py

# Check API logs
cd /workspace/iAvatar
python3 main.py  # Check startup logs

# Test SadTalker directly
cd /workspace/SadTalker
python inference.py --help
```

## 💰 Cost Optimization

### Spot Instance Tips
- Monitor during off-peak hours
- Have backup regions ready
- Use persistent network volumes

### Resource Management
- Stop pods when not in use
- Use smaller instances for development
- Scale up for production

## 🔗 Integration

### Get Your API URL
```bash
# Your API will be available at:
http://[POD_PUBLIC_IP]:8000

# Use this URL in your frontend applications
```

### Example Frontend Integration
```javascript
// JavaScript example
const generateAvatar = async (imageFile, audioFile) => {
  const formData = new FormData()
  formData.append('image', imageFile)
  formData.append('audio', audioFile)
  
  const response = await fetch('http://[POD_IP]:8000/generate-avatar', {
    method: 'POST',
    body: formData
  })
  
  return response.blob() // Returns MP4 video
}
```

## 📞 Support

### Common Issues
1. **Spot instance terminated**: Deploy new instance with same network volume
2. **Models not found**: Re-run `bash scripts/download_models.sh`
3. **GPU memory error**: Restart pod or reduce batch size
4. **API timeout**: Increase timeout settings for large files

### Resources
- [SadTalker GitHub](https://github.com/OpenTalker/SadTalker)
- [RunPod Documentation](https://docs.runpod.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

🎉 **Success!** Your SadTalker API should now be running and ready for integration with your iSpeak application.