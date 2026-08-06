"""Clear the persistent LaTeX SVG cache."""
import shutil, os

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex_cache")

if os.path.exists(CACHE_DIR):
    n = len(os.listdir(CACHE_DIR))
    shutil.rmtree(CACHE_DIR)
    print(f"Deleted tex_cache/ ({n} files)")
else:
    print("tex_cache/ does not exist — nothing to clear")
