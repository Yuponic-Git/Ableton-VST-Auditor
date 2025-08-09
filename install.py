#!/usr/bin/env python3
"""
Ableton VST Auditor Installation Script
Checks system requirements and provides setup instructions.
"""

import sys
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_python_version():
    """Check if Python version is adequate."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        return True, f"{version.major}.{version.minor}.{version.micro}"
    return False, f"{version.major}.{version.minor}.{version.micro}"

def test_tkinter():
    """Test if Tkinter is available for GUI."""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.destroy()
        return True, "Available"
    except Exception as e:
        return False, str(e)

def test_required_modules():
    """Test if all required modules are available."""
    required_modules = ['gzip', 'xml.etree.ElementTree', 'os', 'sys', 'argparse', 'collections', 'datetime', 'threading']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    return len(missing) == 0, missing

def main():
    print("Ableton VST Auditor - Installation Check")
    print("=" * 50)
    print()
    
    # Check Python version
    python_ok, python_version = check_python_version()
    print(f"Python Version: {python_version}")
    if python_ok:
        print("✅ Python version is compatible")
    else:
        print("❌ Python 3.6 or higher required")
        print("   Please update Python from https://python.org/downloads/")
        return False
    
    print()
    
    # Check required modules
    modules_ok, missing_modules = test_required_modules()
    if modules_ok:
        print("✅ All required Python modules available")
    else:
        print("❌ Missing required modules:")
        for module in missing_modules:
            print(f"   - {module}")
        return False
    
    print()
    
    # Check Tkinter for GUI
    tkinter_ok, tkinter_status = test_tkinter()
    if tkinter_ok:
        print("✅ Tkinter available - GUI mode supported")
    else:
        print("⚠️  Tkinter not available - GUI mode not supported")
        print("   Command-line mode will still work")
        print(f"   Error: {tkinter_status}")
    
    print()
    
    # Platform-specific instructions
    system = platform.system()
    print(f"Platform: {system}")
    print()
    
    if system == "Windows":
        print("🪟 Windows Instructions:")
        print("   GUI Mode:  python ableton_vst_audit.py")
        print("   CLI Mode:  python ableton_vst_audit.py --cli \"C:\\Path\\To\\Projects\"")
    elif system == "Darwin":  # macOS
        print("🍎 macOS Instructions:")
        print("   GUI Mode:  python3 ableton_vst_audit.py")
        print("   CLI Mode:  python3 ableton_vst_audit.py --cli \"/Users/YourName/Music/Ableton\"")
    else:  # Linux and others
        print("🐧 Linux Instructions:")
        print("   GUI Mode:  python3 ableton_vst_audit.py")
        print("   CLI Mode:  python3 ableton_vst_audit.py --cli \"/home/user/ableton-projects\"")
    
    print()
    print("✅ Installation check complete!")
    print()
    print("Next steps:")
    print("1. Save 'ableton_vst_audit.py' to your desired location")
    print("2. Run using the appropriate command above")
    print("3. For GUI mode, just double-click the .py file (on some systems)")
    print()
    
    if tkinter_ok:
        try:
            # Show a simple success message in GUI
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(
                "Installation Check Complete", 
                "✅ All requirements met!\n\n"
                "The Ableton VST Auditor is ready to run.\n\n"
                f"Platform: {system}\n"
                f"Python: {python_version}\n"
                "GUI Mode: Supported"
            )
            root.destroy()
        except:
            pass  # If GUI fails, we already showed console output
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nPress Enter to exit...")
        sys.exit(1)