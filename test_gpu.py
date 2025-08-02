#!/usr/bin/env python3
"""
GPU Test Script for iAvatar SadTalker API
Tests GPU availability, CUDA setup, and PyTorch compatibility
"""

import sys
import subprocess
import importlib.util

def check_module(module_name):
    """Check if a Python module is available"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def run_command(cmd, description):
    """Run a system command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timeout"
    except Exception as e:
        return False, "", str(e)

def test_nvidia_drivers():
    """Test NVIDIA drivers and GPU detection"""
    print("🔍 Testing NVIDIA GPU...")
    
    success, stdout, stderr = run_command("nvidia-smi", "NVIDIA System Management Interface")
    
    if success:
        print("✅ NVIDIA drivers working")
        # Extract GPU info
        lines = stdout.split('\n')
        for line in lines:
            if 'GeForce' in line or 'Tesla' in line or 'Quadro' in line or 'RTX' in line:
                gpu_info = line.strip()
                print(f"   🎮 GPU: {gpu_info}")
                break
        return True
    else:
        print("❌ NVIDIA drivers not working")
        print(f"   Error: {stderr}")
        return False

def test_pytorch_cuda():
    """Test PyTorch CUDA availability"""
    print("\n🔍 Testing PyTorch CUDA...")
    
    if not check_module("torch"):
        print("❌ PyTorch not installed")
        print("   Install with: pip install torch")
        return False
    
    try:
        import torch
        
        print(f"✅ PyTorch version: {torch.__version__}")
        
        # Test CUDA availability
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print("✅ CUDA available in PyTorch")
            
            # GPU details
            device_count = torch.cuda.device_count()
            print(f"   🎮 GPU count: {device_count}")
            
            for i in range(device_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"   🎮 GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
            
            # Test tensor operations
            try:
                x = torch.randn(100, 100).cuda()
                y = torch.randn(100, 100).cuda()
                z = torch.mm(x, y)
                print("✅ GPU tensor operations working")
                return True
            except Exception as e:
                print(f"❌ GPU tensor operations failed: {e}")
                return False
        else:
            print("❌ CUDA not available in PyTorch")
            print("   Possible issues:")
            print("   - CUDA drivers not installed")
            print("   - PyTorch CPU-only version")
            print("   - CUDA version mismatch")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import PyTorch: {e}")
        return False
    except Exception as e:
        print(f"❌ PyTorch CUDA test failed: {e}")
        return False

def test_cuda_version():
    """Test CUDA installation and version"""
    print("\n🔍 Testing CUDA installation...")
    
    # Test nvcc (CUDA compiler)
    success, stdout, stderr = run_command("nvcc --version", "CUDA compiler")
    
    if success:
        # Extract CUDA version
        for line in stdout.split('\n'):
            if 'release' in line.lower():
                print(f"✅ CUDA compiler: {line.strip()}")
                break
    else:
        print("⚠️  CUDA compiler (nvcc) not found")
        print("   This is okay if using PyTorch binaries")
    
    # Test nvidia-ml-py for GPU monitoring
    if check_module("pynvml"):
        try:
            import pynvml
            pynvml.nvmlInit()
            driver_version = pynvml.nvmlSystemGetDriverVersion()
            print(f"✅ NVIDIA driver version: {driver_version}")
            
            device_count = pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                print(f"   🎮 {name}: {memory_info.total / 1024**3:.1f} GB total memory")
                
        except Exception as e:
            print(f"⚠️  pynvml error: {e}")
    else:
        print("ℹ️  pynvml not installed (optional)")

def test_ml_libraries():
    """Test ML/AI libraries needed for SadTalker"""
    print("\n🔍 Testing ML libraries...")
    
    libraries = {
        'opencv-python': 'cv2',
        'numpy': 'numpy', 
        'pillow': 'PIL',
        'scipy': 'scipy',
        'matplotlib': 'matplotlib',
        'imageio': 'imageio',
        'librosa': 'librosa',
        'face-alignment': 'face_alignment',
        'gfpgan': 'gfpgan'
    }
    
    installed = []
    missing = []
    
    for package, module in libraries.items():
        if check_module(module):
            try:
                mod = __import__(module)
                version = getattr(mod, '__version__', 'unknown')
                print(f"✅ {package}: {version}")
                installed.append(package)
            except:
                print(f"✅ {package}: installed")
                installed.append(package)
        else:
            print(f"❌ {package}: missing")
            missing.append(package)
    
    return len(missing) == 0, missing

def test_system_info():
    """Display system information"""
    print("\n🔍 System Information...")
    
    # Python version
    print(f"🐍 Python: {sys.version}")
    
    # Platform info
    try:
        import platform
        print(f"💻 OS: {platform.system()} {platform.release()}")
        print(f"🏗️  Architecture: {platform.machine()}")
    except:
        pass
    
    # CPU info
    try:
        import psutil
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        print(f"🧠 CPU: {cpu_count} cores ({cpu_count_logical} threads)")
        
        memory = psutil.virtual_memory()
        print(f"💾 RAM: {memory.total / 1024**3:.1f} GB total")
    except ImportError:
        print("ℹ️  psutil not available for detailed system info")

def main():
    """Run all GPU and system tests"""
    print("🧪 iAvatar GPU Test Suite")
    print("=" * 50)
    
    # Test results
    results = {
        'nvidia_drivers': False,
        'pytorch_cuda': False,
        'ml_libraries': False
    }
    
    # Run tests
    test_system_info()
    results['nvidia_drivers'] = test_nvidia_drivers()
    results['pytorch_cuda'] = test_pytorch_cuda()
    test_cuda_version()
    ml_ok, missing_libs = test_ml_libraries()
    results['ml_libraries'] = ml_ok
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    
    all_passed = all(results.values())
    
    if results['nvidia_drivers']:
        print("✅ GPU Hardware: Ready")
    else:
        print("❌ GPU Hardware: Failed")
    
    if results['pytorch_cuda']:
        print("✅ PyTorch CUDA: Ready") 
    else:
        print("❌ PyTorch CUDA: Failed")
    
    if results['ml_libraries']:
        print("✅ ML Libraries: Ready")
    else:
        print("❌ ML Libraries: Missing packages")
        if missing_libs:
            print(f"   Install: pip install {' '.join(missing_libs)}")
    
    print()
    if all_passed:
        print("🎉 All tests passed! Ready for SadTalker.")
    else:
        print("⚠️  Some tests failed. Check errors above.")
        
        # Recommendations
        print("\n🔧 Recommendations:")
        if not results['nvidia_drivers']:
            print("   - Install NVIDIA drivers")
            print("   - Check GPU is properly connected")
        
        if not results['pytorch_cuda']:
            print("   - Install PyTorch with CUDA support:")
            print("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        
        if not results['ml_libraries']:
            print("   - Install missing packages with:")
            print("     pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)