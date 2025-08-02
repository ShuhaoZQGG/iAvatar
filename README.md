# iAvatar - SadTalker API Service

A FastAPI service that wraps SadTalker for generating talking head videos from images and audio.

## Quick Start on RunPod

### 1. Deploy Pod
- Choose **RTX 4090** (24GB VRAM)
- Template: **PyTorch 2.1** or **Ubuntu 22.04**
- Storage: **50GB+** container disk
- Expose ports: **8000** (API), **22** (SSH)

### 2. Setup
```bash
# SSH into your pod
ssh root@[POD_IP] -p [POD_PORT]

# Run setup script
wget https://raw.githubusercontent.com/YOUR_USERNAME/iAvatar/main/setup_runpod.sh
chmod +x setup_runpod.sh
./setup_runpod.sh
```

### 3. Start Service
```bash
cd /workspace/iAvatar
python3 main.py
```

### 4. Test API
```bash
curl http://[POD_IP]:8000/health
```

## API Endpoints

### `POST /generate-avatar`
Generate talking head video (synchronous)

**Parameters:**
- `image`: Image file (JPG/PNG)
- `audio`: Audio file (WAV/MP3)
- `preprocess`: "crop" | "resize" | "full" (default: "crop")
- `still`: boolean (default: false)
- `use_enhancer`: boolean (default: false)

**Response:** MP4 video file

### `POST /generate-avatar-async`
Start generation job (asynchronous)

**Returns:** `{"job_id": "uuid", "status": "processing"}`

### `GET /job/{job_id}`
Get job result or status

**Returns:** MP4 file if ready, or status JSON

### `GET /health`
Service health check

## Development

### Local Docker
```bash
# Build image
docker build -t iavatar-api .

# Run with GPU
docker run --gpus all -p 8000:8000 iavatar-api
```

### Docker Compose
```bash
docker-compose up
```

## Cost Estimation

**RunPod RTX 4090:**
- Development: $0.34-0.79/hour
- Production: ~$250-400/month (persistent)

**Usage:**
- ~3-5 seconds per video generation
- Supports concurrent requests
- Auto-cleanup of temporary files

## Troubleshooting

### GPU Issues
```bash
# Check GPU
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"
```

### Model Download
```bash
cd /workspace/SadTalker
bash scripts/download_models.sh
```

### Port Access
- Ensure port 8000 is exposed in RunPod
- Check firewall settings
- Use pod's public IP for external access