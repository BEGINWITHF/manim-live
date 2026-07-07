from manim import *
import sys

sq = Square(side_length=1.0, color=BLUE)
sq.set_fill(BLUE, opacity=0.6)
print("MRO:", [c.__name__ for c in type(sq).__mro__])
print("isinstance Square:", isinstance(sq, Square))
print("isinstance Rectangle:", isinstance(sq, Rectangle))
print("isinstance Polygon:", isinstance(sq, Polygon))
print("isinstance Polygram:", isinstance(sq, Polygram))

tri = Triangle(color=YELLOW)
tri.set_fill(YELLOW, opacity=0.6)
print("\nTriangle MRO:", [c.__name__ for c in type(tri).__mro__])
print("isinstance Triangle:", isinstance(tri, Triangle))
print("isinstance Polygon:", isinstance(tri, Polygon))
print("isinstance Polygram:", isinstance(tri, Polygram))

rect = Rectangle(width=1.6, height=0.9, color=GREEN)
rect.set_fill(GREEN, opacity=0.6)
print("\nRectangle MRO:", [c.__name__ for c in type(rect).__mro__])
print("isinstance Rectangle:", isinstance(rect, Rectangle))
print("isinstance Polygon:", isinstance(rect, Polygon))
print("isinstance Polygram:", isinstance(rect, Polygram))
