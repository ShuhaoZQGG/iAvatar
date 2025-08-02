#!/usr/bin/env python3
"""
Test script using SadTalker official examples to test the iAvatar API
"""

import os
import requests
import shutil

def get_sadtalker_examples():
    """Get SadTalker official example files"""
    sadtalker_path = "/workspace/SadTalker"
    
    # Available example images
    image_examples = [
        "happy.png",
        "sad.png", 
        "happy1.png",
        "sad1.png",
        "people_0.png"
    ]
    
    # Available example audio files
    audio_examples = [
        "bus_chinese.wav",
        "RD_Radio31_000.wav"
    ]
    
    # Check what's actually available
    available_images = []
    available_audio = []
    
    for img in image_examples:
        img_path = os.path.join(sadtalker_path, "examples", "source_image", img)
        if os.path.exists(img_path):
            available_images.append(img_path)
    
    for aud in audio_examples:
        aud_path = os.path.join(sadtalker_path, "examples", "driven_audio", aud)
        if os.path.exists(aud_path):
            available_audio.append(aud_path)
    
    return available_images, available_audio

def copy_test_files():
    """Copy SadTalker examples to current directory for testing"""
    available_images, available_audio = get_sadtalker_examples()
    
    if not available_images:
        print("❌ No SadTalker example images found!")
        print("Make sure SadTalker is installed at /workspace/SadTalker")
        return None, None
    
    if not available_audio:
        print("❌ No SadTalker example audio found!")
        print("Make sure SadTalker is installed at /workspace/SadTalker")
        return None, None
    
    # Use first available files
    source_image = available_images[0]
    source_audio = available_audio[0]
    
    # Copy to current directory
    test_image = "test_face.png"
    test_audio = "test_speech.wav"
    
    shutil.copy2(source_image, test_image)
    shutil.copy2(source_audio, test_audio)
    
    print(f"📷 Using image: {os.path.basename(source_image)}")
    print(f"🎵 Using audio: {os.path.basename(source_audio)}")
    print(f"📁 Copied to: {test_image}, {test_audio}")
    
    return test_image, test_audio

def test_api(api_url, image_file, audio_file):
    """Test the SadTalker API"""
    print(f"\n🌐 Testing API at: {api_url}")
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{api_url}/health", timeout=10)
        print(f"✅ Health check: {health_response.status_code}")
        health_data = health_response.json()
        print(f"   GPU available: {health_data.get('gpu_available', 'unknown')}")
        print(f"   SadTalker initialized: {health_data.get('sadtalker_initialized', 'unknown')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test avatar generation
    try:
        print(f"\n🎬 Testing avatar generation...")
        print(f"   Image: {os.path.basename(image_file)}")
        print(f"   Audio: {os.path.basename(audio_file)}")
        
        # Determine file types
        img_ext = os.path.splitext(image_file)[1].lower()
        aud_ext = os.path.splitext(audio_file)[1].lower()
        
        img_type = 'image/png' if img_ext == '.png' else 'image/jpeg'
        aud_type = 'audio/wav' if aud_ext == '.wav' else 'audio/mpeg'
        
        with open(image_file, 'rb') as img, open(audio_file, 'rb') as aud:
            files = {
                'image': (os.path.basename(image_file), img, img_type),
                'audio': (os.path.basename(audio_file), aud, aud_type)
            }
            
            print("   📡 Sending request...")
            response = requests.post(
                f"{api_url}/generate-avatar",
                files=files,
                timeout=120  # Give more time for generation
            )
        
        if response.status_code == 200:
            # Save the generated video
            output_file = "generated_avatar.mp4"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"✅ Success! Generated video saved as: {output_file}")
            print(f"   📺 Video size: {size_mb:.1f} MB")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Error details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    print("🧪 iAvatar API Test using SadTalker Examples")
    print("=" * 50)
    
    # Copy SadTalker example files
    print("📋 Looking for SadTalker example files...")
    image_file, audio_file = copy_test_files()
    
    if not image_file or not audio_file:
        print("\n❌ Could not find SadTalker example files.")
        print("Make sure SadTalker is properly installed at /workspace/SadTalker")
        return
    
    print(f"\n📁 Test files ready:")
    print(f"  - Image: {image_file} ({os.path.getsize(image_file)/1024:.1f} KB)")
    print(f"  - Audio: {audio_file} ({os.path.getsize(audio_file)/1024:.1f} KB)")
    
    # Get API URL from user
    api_url = input("\n🌐 Enter your RunPod API URL (default: http://0.0.0.0:8000): ").strip()
    
    if not api_url:
        api_url = "http://0.0.0.0:8000"
        print(f"🔗 Using default URL: {api_url}")
    
    # Remove trailing slash
    api_url = api_url.rstrip('/')
    
    # Test the API
    print(f"\n🚀 Starting API test...")
    success = test_api(api_url, image_file, audio_file)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test completed successfully!")
        print("✅ Your iAvatar SadTalker API is working correctly.")
        print("📺 Check the generated_avatar.mp4 file to see the result.")
    else:
        print("❌ Test failed. Please check your API setup.")
        print("💡 Troubleshooting tips:")
        print("   - Ensure SadTalker API is running")
        print("   - Check if ffmpeg is installed") 
        print("   - Verify GPU is available")
        print("   - Run: python3 test_gpu.py")

if __name__ == "__main__":
    main()