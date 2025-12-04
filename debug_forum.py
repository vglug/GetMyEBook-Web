import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

try:
    print("Attempting to import cps.forum...")
    from cps.forum import get_forum_blueprints
    print("✅ Successfully imported cps.forum")
    
    print("Attempting to get blueprints...")
    blueprints = get_forum_blueprints()
    print(f"✅ Got blueprints: {list(blueprints.keys())}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
