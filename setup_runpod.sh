#!/bin/bash

# RunPod Setup Script for iAvatar SadTalker Service
# Run this script after SSH'ing into your RunPod instance

set -e

echo "🚀 Setting up iAvatar on RunPod..."

# Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install essential tools
echo "🔧 Installing essential tools..."
apt-get install -y \
    git \
    wget \
    curl \
    unzip \
    htop \
    nano \
    tmux \
    tree

# Install Python dependencies
echo "🐍 Setting up Python environment..."
pip install --upgrade pip

# Clone SadTalker repository
echo "📥 Cloning SadTalker repository..."
cd /workspace
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker

# Install SadTalker dependencies
echo "📦 Installing SadTalker dependencies..."
pip install -r requirements.txt

# Download pretrained models
echo "🤖 Downloading pretrained models..."
bash scripts/download_models.sh

# Clone iAvatar service code
echo "📥 Setting up iAvatar service..."
cd /workspace
git clone https://github.com/YOUR_USERNAME/iAvatar.git  # Update this URL
cd iAvatar

# Install FastAPI dependencies
echo "🌐 Installing FastAPI dependencies..."
pip install fastapi uvicorn python-multipart

# Create necessary directories
mkdir -p /workspace/iAvatar/outputs
mkdir -p /workspace/iAvatar/temp

# Set up environment variables
echo "🔧 Setting up environment variables..."
export SADTALKER_PATH="/workspace/SadTalker"
echo 'export SADTALKER_PATH="/workspace/SadTalker"' >> ~/.bashrc

# Test GPU availability
echo "🎮 Testing GPU availability..."
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU count: {torch.cuda.device_count()}')"

# Create a simple test script
cat > test_setup.py << 'EOF'
import torch
import os
import sys

def test_setup():
    print("=== iAvatar Setup Test ===")
    
    # Test CUDA
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU device: {torch.cuda.get_device_name(0)}")
        print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Test SadTalker
    sadtalker_path = "/workspace/SadTalker"
    print(f"SadTalker exists: {os.path.exists(sadtalker_path)}")
    
    # Test FastAPI imports
    try:
        import fastapi
        import uvicorn
        print("FastAPI imports: ✅")
    except ImportError as e:
        print(f"FastAPI imports: ❌ {e}")
    
    # Test SadTalker imports
    sys.path.append(sadtalker_path)
    try:
        # Basic import test - may fail but gives us info
        print("SadTalker path added to sys.path")
    except Exception as e:
        print(f"SadTalker import issue: {e}")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_setup()
EOF

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: python3 test_setup.py"
echo "2. Start the service: cd /workspace/iAvatar && python3 main.py"
echo "3. Test API at: http://[POD_IP]:8000"
echo ""
echo "📝 Notes:"
echo "- Update the git clone URL in this script with your actual repository"
echo "- Make sure to expose port 8000 in RunPod settings"
echo "- Use 'tmux' to keep the service running after disconnecting"