import os
import winshell # Install: pip install winshell pypiwin32
from win32com.client import Dispatch

def create_shortcut():
    desktop = winshell.desktop()
    startup = winshell.startup()
    
    path = os.path.join(os.getcwd(), "Run_VISION.bat")
    target = os.path.join(startup, "VISION_AI.lnk")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(target)
    shortcut.Targetpath = path
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.IconLocation = os.getcwd()
    shortcut.save()
    
    print(f"✅ Success! VISION added to Startup: {target}")

if __name__ == "__main__":
    print("Adding VISION to System Startup...")
    try:
        create_shortcut()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Tip: Run 'pip install winshell pypiwin32' first")
    input("Press Enter to exit...")
