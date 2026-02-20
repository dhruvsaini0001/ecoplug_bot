"""
Quick Start Script
Run this to start the EV Charging Diagnostic Chatbot server.
"""
import subprocess
import sys
import os


def main():
    """Start the FastAPI application."""
    print("=" * 60)
    print("🔌 EV CHARGING DIAGNOSTIC CHATBOT PLATFORM")
    print("=" * 60)
    print()
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("  .env file not found!")
        print("Creating .env from .env.example...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print(" .env file created")
        else:
            print(" .env.example not found. Please create .env manually.")
            return
    
    print("Starting server...")
    print()
    print("API will be available at:")
    print("  • http://localhost:8000")
    print("  • Docs: http://localhost:8000/docs")
    print("  • Health: http://localhost:8000/v1/health")
    print()
    print("Press CTRL+C to stop")
    print("=" * 60)
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "chatbot.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")


if __name__ == "__main__":
    main()
