#!/usr/bin/env python3
"""
Budget Portal Startup Script
This script starts both the FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8, 0):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version} detected")

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting API server...")
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path.cwd())
    
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "APIServer:app", 
        "--host", "127.0.0.1", 
        "--port", "8000", 
        "--reload"
    ], env=env)

def start_streamlit_app():
    """Start the Streamlit app"""
    print("🎨 Starting Streamlit app...")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", 
        "streamlit_app.py", 
        "--server.port", "8501",
        "--server.address", "127.0.0.1"
    ])

def wait_for_api_ready(max_attempts=30):
    """Wait for API server to be ready"""
    import requests
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:8000/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ API server is ready")
                return True
        except:
            pass
        
        time.sleep(1)
        print(f"⏳ Waiting for API server... ({attempt + 1}/{max_attempts})")
    
    print("❌ API server failed to start")
    return False

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down servers...")
    global api_process, streamlit_process
    
    if 'api_process' in globals() and api_process:
        api_process.terminate()
    if 'streamlit_process' in globals() and streamlit_process:
        streamlit_process.terminate()
    
    sys.exit(0)

def main():
    """Main startup function"""
    print("🏢 Budget Portal - Startup Script")
    print("=" * 50)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check environment
    check_python_version()
    
    # Install requirements
    # install_requirements()
    
    global api_process, streamlit_process
    
    try:
        # Start API server
        api_process = start_api_server()
        
        # Wait for API to be ready
        if not wait_for_api_ready():
            api_process.terminate()
            sys.exit(1)
        
        # Start Streamlit app
        streamlit_process = start_streamlit_app()
        
        print("🎉 Both servers started successfully!")
        print("📊 Streamlit app: http://127.0.0.1:8501")
        print("🔗 API server: http://127.0.0.1:8000")
        print("📚 API docs: http://127.0.0.1:8000/docs")
        print("\n🛑 Press Ctrl+C to stop both servers")
        
        # Wait for both processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
            
            if streamlit_process.poll() is not None:
                print("❌ Streamlit app stopped unexpectedly")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal")
    
    finally:
        # Cleanup
        if 'api_process' in locals() and api_process:
            api_process.terminate()
            api_process.wait()
        
        if 'streamlit_process' in locals() and streamlit_process:
            streamlit_process.terminate()
            streamlit_process.wait()
        
        print("✅ Cleanup completed")

if __name__ == "__main__":
    main()
