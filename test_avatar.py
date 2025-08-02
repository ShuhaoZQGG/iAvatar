#!/usr/bin/env python3
"""
Test script to generate sample files and test the SadTalker API
"""

import os
import requests
from PIL import Image, ImageDraw
import numpy as np
from scipy.io.wavfile import write
import tempfile

def create_test_image(filename="test_face.jpg", size=(512, 512)):
    """Create a simple test face image"""
    # Create a basic face-like image
    img = Image.new('RGB', size, color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple face
    # Head (circle)
    head_size = min(size) - 100
    head_x = (size[0] - head_size) // 2
    head_y = (size[1] - head_size) // 2
    draw.ellipse([head_x, head_y, head_x + head_size, head_y + head_size], fill='peachpuff', outline='black', width=2)
    
    # Eyes
    eye_size = 30
    left_eye_x = head_x + head_size // 3
    right_eye_x = head_x + 2 * head_size // 3
    eye_y = head_y + head_size // 3
    draw.ellipse([left_eye_x - eye_size//2, eye_y - eye_size//2, left_eye_x + eye_size//2, eye_y + eye_size//2], fill='white', outline='black')
    draw.ellipse([right_eye_x - eye_size//2, eye_y - eye_size//2, right_eye_x + eye_size//2, eye_y + eye_size//2], fill='white', outline='black')
    
    # Pupils
    pupil_size = 10
    draw.ellipse([left_eye_x - pupil_size//2, eye_y - pupil_size//2, left_eye_x + pupil_size//2, eye_y + pupil_size//2], fill='black')
    draw.ellipse([right_eye_x - pupil_size//2, eye_y - pupil_size//2, right_eye_x + pupil_size//2, eye_y + pupil_size//2], fill='black')
    
    # Nose
    nose_x = head_x + head_size // 2
    nose_y = head_y + head_size // 2
    draw.line([nose_x, nose_y - 20, nose_x, nose_y + 10], fill='black', width=3)
    
    # Mouth
    mouth_y = head_y + 2 * head_size // 3
    mouth_width = 60
    draw.arc([nose_x - mouth_width//2, mouth_y - 15, nose_x + mouth_width//2, mouth_y + 15], 0, 180, fill='black', width=3)
    
    img.save(filename)
    print(f"Created test image: {filename}")
    return filename

def create_test_audio(filename="test_speech.wav", duration=3, sample_rate=22050):
    """Create a simple test audio file with speech-like sounds"""
    # Generate speech-like audio with varying frequencies
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create speech-like pattern with multiple frequencies
    audio = np.zeros_like(t)
    
    # Add formants (speech characteristics)
    formant1 = 0.3 * np.sin(2 * np.pi * 800 * t)  # ~800 Hz
    formant2 = 0.2 * np.sin(2 * np.pi * 1200 * t)  # ~1200 Hz
    formant3 = 0.1 * np.sin(2 * np.pi * 2400 * t)  # ~2400 Hz
    
    # Add some variation to make it more speech-like
    envelope = np.exp(-t * 0.5) * (1 + 0.5 * np.sin(2 * np.pi * 4 * t))
    
    audio = (formant1 + formant2 + formant3) * envelope
    
    # Add some noise for realism
    noise = 0.05 * np.random.normal(0, 1, len(audio))
    audio += noise
    
    # Normalize
    audio = np.clip(audio, -1, 1)
    audio_int = (audio * 32767).astype(np.int16)
    
    write(filename, sample_rate, audio_int)
    print(f"Created test audio: {filename}")
    return filename

def test_api(api_url, image_file, audio_file):
    """Test the SadTalker API"""
    print(f"\nTesting API at: {api_url}")
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{api_url}/health")
        print(f"Health check: {health_response.status_code}")
        print(f"Health data: {health_response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test avatar generation
    try:
        print("\nTesting avatar generation...")
        
        with open(image_file, 'rb') as img, open(audio_file, 'rb') as aud:
            files = {
                'image': ('test_face.jpg', img, 'image/jpeg'),
                'audio': ('test_speech.wav', aud, 'audio/wav')
            }
            
            response = requests.post(
                f"{api_url}/generate-avatar",
                files=files,
                timeout=60  # Give it time to generate
            )
        
        if response.status_code == 200:
            # Save the generated video
            output_file = "generated_avatar.mp4"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"✅ Success! Generated video saved as: {output_file}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    print("🧪 Creating test files for SadTalker API...")
    
    # Create test files
    image_file = create_test_image()
    audio_file = create_test_audio()
    
    print(f"\n📁 Created files:")
    print(f"  - Image: {image_file} ({os.path.getsize(image_file)} bytes)")
    print(f"  - Audio: {audio_file} ({os.path.getsize(audio_file)} bytes)")
    
    # Get API URL from user
    api_url = input("\n🌐 Enter your RunPod API URL (e.g., http://123.456.789.10:8000): ").strip()
    
    if not api_url:
        print("❌ No API URL provided")
        return
    
    # Remove trailing slash
    api_url = api_url.rstrip('/')
    
    # Test the API
    success = test_api(api_url, image_file, audio_file)
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("Your SadTalker API is working correctly.")
    else:
        print("\n❌ Test failed. Please check your API setup.")

if __name__ == "__main__":
    main()