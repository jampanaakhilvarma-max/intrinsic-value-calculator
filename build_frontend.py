#!/usr/bin/env python3
"""
Build script for React frontend
This script builds the React app and moves it to a location where FastAPI can serve it
"""
import os
import subprocess
import shutil
import sys

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, cwd=cwd, 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error running command: {command}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        print(f"✅ Success: {command}")
        if result.stdout:
            print(f"Output: {result.stdout[:200]}...")  # Print first 200 chars
        return True
    except Exception as e:
        print(f"❌ Exception running command {command}: {e}")
        return False

def main():
    # Change to the project directory
    project_dir = os.path.join(os.path.dirname(__file__), "project")
    
    if not os.path.exists(project_dir):
        print("❌ React project directory not found!")
        print(f"Looking for: {project_dir}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Directory contents: {os.listdir('.')}")
        return False
    
    print("� Building React frontend...")
    
    # Build the React app (npm install should have been done in nixpacks build phase)
    print("🚀 Building React app...")
    if not run_command("npm run build", cwd=project_dir):
        return False
    
    # Check if dist folder exists (Vite builds to 'dist')
    dist_dir = os.path.join(project_dir, "dist")
    if not os.path.exists(dist_dir):
        print(f"❌ Build directory 'dist' not found at: {dist_dir}")
        print(f"Project directory contents: {os.listdir(project_dir)}")
        return False
    
    # Create static directory for FastAPI
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        shutil.rmtree(static_dir)
    
    # Copy build files to static directory
    print("📁 Copying build files to static directory...")
    shutil.copytree(dist_dir, static_dir)
    
    print("✅ Frontend build completed successfully!")
    print(f"📂 Static files are in: {static_dir}")
    print(f"Static directory contents: {os.listdir(static_dir)[:10]}...")  # Show first 10 files
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("❌ Build failed!")
        sys.exit(1)
    else:
        print("✅ Build completed successfully!")