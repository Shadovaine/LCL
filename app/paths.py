#=================================
# Path utilities for finding the commands directory
#=================================

from pathlib import Path
import os
import sys

def _find_commands_base() -> Path:
    """Find the base directory containing command YAML files."""
    
    print(f"[DEBUG] Looking for commands directory...", file=sys.stderr)
    
    # Try several possible locations
    possible_locations = []
    
    # 1. Relative to the app directory (project structure: project/app/ and project/data/commands/)
    app_dir = Path(__file__).parent  # This is the 'app' directory
    project_root = app_dir.parent    # Go up one level to project root
    
    # Based on your structure: ~/GitHub/Linux-Command-Library-dev/data/commands
    possible_locations.extend([
        project_root / "data" / "commands",  # This should be correct
        project_root / "commands",
        Path.home() / "GitHub" / "Linux-Command-Library-dev" / "data" / "commands",
        Path("/usr/share/lcl/commands"),
        Path("/opt/lcl/commands"),
    ])
    
    # Check environment variable
    env_path = os.getenv("LCL_COMMANDS_PATH")
    if env_path:
        possible_locations.insert(0, Path(env_path))
    
    print(f"[DEBUG] Searching locations:", file=sys.stderr)
    for location in possible_locations:
        print(f"[DEBUG]   - {location}", file=sys.stderr)
        if location.exists() and location.is_dir():
            # Check if it contains expected category folders
            expected_categories = ["File_Directory_Mgmt", "Archive_Compression_Mgmt", "System_Administration"]
            found_categories = [d.name for d in location.iterdir() if d.is_dir()]
            
            if any(cat in found_categories for cat in expected_categories):
                print(f"[DEBUG] Found commands directory: {location}", file=sys.stderr)
                return location
    
    raise FileNotFoundError("Could not find commands directory")
