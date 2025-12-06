
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, '/home/vasanth/Desktop/GetMyEBook-Web')

try:
    print("Attempting to import cps.forum...")
    from cps.forum import init_forum_extensions, get_forum_blueprints
    print("Import successful!")
    
    print("Attempting to get blueprints...")
    blueprints = get_forum_blueprints()
    print("Blueprints found:", blueprints.keys())
    
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
