from setuptools import setup, find_packages

setup(
    name="manim_vulkan",
    version="0.1.0",
    author="Your Name",
    description="Vulkan renderer plugin for Manim",
    packages=find_packages(),
    install_requires=[
        "manim>=0.18.0",
        "vulkan",
        "glfw",
        "numpy",
    ],
    python_requires=">=3.8",
)