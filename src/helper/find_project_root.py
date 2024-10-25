from pathlib import Path

def find_project_root(project_name):
    current_dir = Path(__file__).resolve().parent

    # Traverse upwards until we find the directory with the project name
    while current_dir.name != project_name:
        if current_dir.parent == current_dir:  # We've reached the root of the file system
            raise FileNotFoundError(f"Project root '{project_name}' not found")
        current_dir = current_dir.parent

    return current_dir