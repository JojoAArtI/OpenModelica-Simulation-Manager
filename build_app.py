"""One-click PyInstaller build script for OpenModelica Simulation Manager.

Usage:
    python build_app.py
"""

import sys
import subprocess
from pathlib import Path


def main():
    print("==========================================================")
    print(" Building OpenModelica Simulation Manager Executable      ")
    print("==========================================================")

    project_root = Path(__file__).resolve().parent
    main_py = project_root / "src" / "main.py"
    resources_dir = project_root / "resources"
    icon_path = resources_dir / "icons" / ("openmodelica.ico" if sys.platform == "win32" else "openmodelica.png")

    if not main_py.exists():
        print(f"[ERROR] main.py not found at: {main_py}")
        sys.exit(1)

    # Prepare PyInstaller Arguments
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=OpenModelicaSimulationManager",
        "--onefile",
        "--windowed",
        f"--add-data={resources_dir}{';' if sys.platform == 'win32' else ':'}resources",
        f"--icon={icon_path}",
        "--clean",
        str(main_py),
    ]

    print(f"[BUILD INFO] Executing PyInstaller command:\n{' '.join(cmd)}\n")

    try:
        res = subprocess.run(cmd, check=True)
        if res.returncode == 0:
            dist_exe = project_root / "dist" / ("OpenModelicaSimulationManager.exe" if sys.platform == "win32" else "OpenModelicaSimulationManager")
            print("\n==========================================================")
            print(" BUILD SUCCESSFUL!")
            print(f" Executable created at: {dist_exe.resolve()}")
            print("==========================================================")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] PyInstaller build failed with exit code {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
