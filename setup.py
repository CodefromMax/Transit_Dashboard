import sys
import os

# Dynamically get the project root (assuming this script is in 'src/prepare_data/census')
project_root = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')

# Add 'src' to the PYTHONPATH
print(src_path)