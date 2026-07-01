import sys
from scenes.demo_scene import TestTransform, TestTransformMatchingShapes, TestFadeTransform

SCENES = {
    "1": ("Transform", TestTransform),
    "2": ("TransformMatchingShapes", TestTransformMatchingShapes),
    "3": ("FadeTransform", TestFadeTransform),
}

def main():
    if len(sys.argv) > 1:
        key = sys.argv[1]
    else:
        print("Select test:")
        for k, (name, _) in SCENES.items():
            print(f"  {k} - {name}")
        key = input("Choice: ").strip()

    if key in SCENES:
        name, cls = SCENES[key]
        print(f"Running: {name}")
        scene = cls()
        scene.construct()
    else:
        print(f"Invalid choice: {key}")

if __name__ == "__main__":
    main()
