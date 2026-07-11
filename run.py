"""
Main Entry Point
================
Run this file to start the application
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main entry point"""
    
    print("\n" + "="*60)
    print("🩺 AI Medical Assistant - Starting...")
    print("="*60 + "\n")
    
    # Check data directory
    from src.config import DATA_DIR
    if not os.path.exists(DATA_DIR):
        print(f"❌ Data directory not found: {DATA_DIR}")
        print("   Please create it and add your data files.")
        return
    
    data_files = os.listdir(DATA_DIR)
    if not data_files:
        print(f"⚠️  Data directory is empty: {DATA_DIR}")
        print("   Please add PDF, TXT, or CSV files.")
        return
    
    print(f"📁 Found {len(data_files)} file(s) in data directory:")
    for f in data_files:
        print(f"   - {f}")
    print()
    
    # Launch Streamlit
    import streamlit.web.cli as stcli
    sys.argv = ["streamlit", "run", "app.py", "--server.port", "8501"]
    stcli.main()


if __name__ == "__main__":
    main()