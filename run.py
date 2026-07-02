import sys
from scenes.demo_scene import TestTransform, TestTransformMatchingShapes, TestFadeTransform

SCENES = {
    "1": TestTransform,
    "2": TestTransformMatchingShapes,
    "3": TestFadeTransform,
}

def main():
    num = sys.argv[1] if len(sys.argv) > 1 else "1"
    cls = SCENES.get(num)
    if cls is None:
        print(f"Usage: python run.py <1|2|3>")
        sys.exit(1)
    print(f"Running: {cls.__name__}")
    scene = cls()
    scene.construct()

if __name__ == "__main__":
    main()
