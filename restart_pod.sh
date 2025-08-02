#!/bin/bash

# RunPod Restart Script for iAvatar SadTalker API
# Run this script every time you restart/redeploy your pod

set -e  # Exit on any error

echo "🚀 iAvatar RunPod Restart Script"
echo "=================================="

# Function to print colored output
print_status() {
    echo -e "\033[1;34m$1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

# Check if we're in the right directory
if [ ! -d "/workspace" ]; then
    print_error "Not in RunPod environment - /workspace not found"
    exit 1
fi

cd /workspace

print_status "Step 1: Installing system dependencies..."
# Update package list and install ffmpeg
apt update > /dev/null 2>&1
apt install -y ffmpeg > /dev/null 2>&1
print_success "ffmpeg installed"

# Verify ffmpeg
if command -v ffmpeg &> /dev/null; then
    print_success "ffmpeg verified: $(ffmpeg -version | head -n 1 | cut -d' ' -f3)"
else
    print_error "ffmpeg installation failed"
    exit 1
fi

print_status "Step 2: Setting up SadTalker..."
# Check if SadTalker exists (should be on network volume)
if [ -d "/workspace/SadTalker" ]; then
    print_success "SadTalker directory found"
    cd /workspace/SadTalker
    
    # Check if models exist
    if [ -d "checkpoints" ] && [ "$(ls -A checkpoints)" ]; then
        print_success "SadTalker models found ($(ls checkpoints | wc -l) files)"
    else
        print_warning "SadTalker models missing - downloading..."
        bash scripts/download_models.sh
        print_success "SadTalker models downloaded"
    fi
    
    # Install SadTalker requirements
    print_status "Installing SadTalker requirements..."
    pip install -r requirements.txt > /dev/null 2>&1
    print_success "SadTalker requirements installed"
    
    # Test SadTalker briefly
    print_status "Testing SadTalker..."
    if python inference.py --help > /dev/null 2>&1; then
        print_success "SadTalker working"
    else
        print_error "SadTalker test failed"
        exit 1
    fi
    
else
    print_error "SadTalker not found - please check network volume mounting"
    print_warning "Expected at: /workspace/SadTalker"
    exit 1
fi

print_status "Step 3: Setting up iAvatar API..."
# Check if iAvatar exists
if [ -d "/workspace/iAvatar" ]; then
    print_success "iAvatar directory found"
    cd /workspace/iAvatar
    
    # Pull latest changes
    print_status "Updating iAvatar code..."
    git pull origin master > /dev/null 2>&1 || print_warning "Git pull failed - using existing code"
    
else
    print_status "Cloning iAvatar repository..."
    cd /workspace
    git clone https://github.com/ShuhaoZQGG/iAvatar.git
    cd iAvatar
    print_success "iAvatar cloned"
fi

# Install critical packages first
print_status "Installing critical FastAPI packages..."
pip install fastapi uvicorn python-multipart > /dev/null 2>&1
print_success "FastAPI packages installed"

# Install all requirements
print_status "Installing iAvatar requirements..."
pip install -r requirements.txt > /dev/null 2>&1
print_success "iAvatar requirements installed"

# Create necessary directories
mkdir -p /workspace/iAvatar/outputs
mkdir -p /workspace/iAvatar/temp
print_success "Output directories created"

# Set environment variables
export SADTALKER_PATH="/workspace/SadTalker"
export OUTPUT_DIR="/workspace/iAvatar/outputs"
export TEMP_DIR="/workspace/iAvatar/temp"

print_status "Step 4: Running system tests..."
# Test GPU
print_status "Testing GPU..."
if python3 test_gpu.py | grep -q "All tests passed"; then
    print_success "GPU tests passed"
else
    print_warning "GPU tests failed - check test_gpu.py output"
fi

# Test API health (quick start and stop)
print_status "Testing API startup..."
timeout 10s python3 main.py > /tmp/api_test.log 2>&1 &
API_PID=$!
sleep 3

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "API startup test passed"
    kill $API_PID 2>/dev/null || true
else
    print_warning "API startup test failed - check manually"
    kill $API_PID 2>/dev/null || true
fi

print_status "Step 5: Final verification..."
# Check all critical components
CHECKS=(
    "ffmpeg:$(command -v ffmpeg)"
    "SadTalker:$([ -d /workspace/SadTalker ] && echo 'found' || echo 'missing')"
    "Models:$([ -d /workspace/SadTalker/checkpoints ] && echo 'found' || echo 'missing')"
    "iAvatar:$([ -d /workspace/iAvatar ] && echo 'found' || echo 'missing')"
    "Python packages:$(python3 -c 'import torch, fastapi, uvicorn' 2>/dev/null && echo 'ok' || echo 'missing')"
)

echo ""
echo "🔍 System Status:"
echo "=================="
for check in "${CHECKS[@]}"; do
    name="${check%%:*}"
    status="${check##*:}"
    if [[ "$status" == *"missing"* ]] || [[ "$status" == *"not found"* ]]; then
        print_error "$name: $status"
    else
        print_success "$name: $status"
    fi
done

echo ""
print_status "Step 6: Ready to start!"
echo "🌐 To start the API server:"
echo "   cd /workspace/iAvatar"
echo "   python3 main.py"
echo ""
echo "🧪 To test the API:"
echo "   python3 test_avatar.py"
echo ""
echo "📊 To check GPU status:"
echo "   python3 test_gpu.py"
echo ""
echo "🔗 API will be available at:"
echo "   http://0.0.0.0:8000 (local)"
echo "   http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_POD_IP'):8000 (external)"
echo ""

# Save restart info
cat > /workspace/restart_info.txt << EOF
Last restart: $(date)
SadTalker: /workspace/SadTalker
iAvatar: /workspace/iAvatar
API URL: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_POD_IP'):8000
EOF

print_success "Restart script completed successfully!"
print_status "Logs saved to /workspace/restart_info.txt"

# Optional: Auto-start API in tmux
read -p "🤖 Start API server automatically in tmux? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v tmux &> /dev/null; then
        tmux new-session -d -s iavatar -c /workspace/iAvatar
        tmux send-keys -t iavatar "python3 main.py" Enter
        print_success "API started in tmux session 'iavatar'"
        echo "📺 To attach: tmux attach -t iavatar"
        echo "📺 To detach: Ctrl+B then D"
    else
        print_warning "tmux not available - start API manually"
    fi
fi

echo ""
print_success "🎉 All done! Your iAvatar API is ready to use."