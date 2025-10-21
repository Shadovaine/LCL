#=================================
# YAML loading functions for Linux Command Library
#=================================

#---------------Standard Library---------------
from typing import Any, Dict, List
from pathlib import Path
import yaml
import sys

#---------------Local---------------
from .paths import _find_commands_base
from .models import ALLOWED_CATEGORIES, STRICT_CATEGORIES

def load_all_commands() -> List[Dict[str, Any]]:
    """Load all commands from YAML files in category directories."""
    print(f"[DEBUG] === Starting load_all_commands ===", file=sys.stderr)
    
    commands = []
    
    # Try multiple possible paths
    possible_paths = [
        Path(__file__).parent / "data" / "commands",
        Path(__file__).parent.parent / "data" / "commands",
        Path("data") / "commands",
    ]
    
    data_dir = None
    for path in possible_paths:
        if path.exists():
            data_dir = path
            break
    
    if not data_dir:
        print(f"[ERROR] Could not find data/commands directory", file=sys.stderr)
        return []
    
    print(f"[DEBUG] Using data directory: {data_dir}", file=sys.stderr)

    docs: List[Dict[str, Any]] = []
    
    # Get all category directories
    try:
        category_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
        print(f"[DEBUG] Found category directories: {[d.name for d in category_dirs]}", file=sys.stderr)
        
        if not category_dirs:
            print(f"[WARN] No category directories found in {data_dir}", file=sys.stderr)
            return []
            
    except Exception as e:
        print(f"[ERROR] Error listing category directories: {e}", file=sys.stderr)
        return []

    # Process each category directory
    total_yaml_files = 0
    for cat_dir in sorted(category_dirs):
        category_name = cat_dir.name
        print(f"[DEBUG] Processing category: {category_name}", file=sys.stderr)
        
        # Find YAML files in this category
        try:
            yml_files = list(cat_dir.glob("*.yml"))
            yaml_files = list(cat_dir.glob("*.yaml"))
            all_yaml_files = yml_files + yaml_files
            
            print(f"[DEBUG] Found {len(all_yaml_files)} YAML files in {category_name}", file=sys.stderr)
            total_yaml_files += len(all_yaml_files)
            
            # Process each YAML file
            for yml_file in sorted(all_yaml_files):
                try:
                    with open(yml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                    
                    if not data or not isinstance(data, dict):
                        print(f"[WARN] Invalid YAML data in {yml_file}", file=sys.stderr)
                        continue

                    # Ensure required fields
                    if not data.get("name"):
                        print(f"[WARN] Missing 'name' field in {yml_file}", file=sys.stderr)
                        continue

                    # Set category from directory name if not present
                    if "category" not in data or not data["category"]:
                        data["category"] = category_name

                    # Add metadata
                    data["_source_file"] = str(yml_file)
                    data["_category_dir"] = category_name

                    docs.append(data)
                    print(f"[DEBUG] Loaded: {data.get('name')}", file=sys.stderr)
                    
                except Exception as e:
                    print(f"[ERROR] Error loading {yml_file}: {e}", file=sys.stderr)
                    continue
                
        except Exception as e:
            print(f"[ERROR] Error processing category {category_name}: {e}", file=sys.stderr)
            continue

    print(f"[DEBUG] === Finished loading {len(docs)} commands from {total_yaml_files} YAML files ===", file=sys.stderr)
    return docs