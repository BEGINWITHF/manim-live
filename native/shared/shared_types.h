#ifndef SHARED_TYPES_H
#define SHARED_TYPES_H

#ifndef MAX_SHAPES
#define MAX_SHAPES 4096
#endif

typedef struct {
    float x, y, hw, hh, rot;
    int r, g, b;
} Rect;

typedef struct {
    float x, y, radius;
    int r, g, b;
} Circle;

typedef struct {
    float x1, y1, x2, y2;
    int width, r, g, b;
} LineObj;

typedef struct {
    char text[256];
    float x, y;
    int size, r, g, b;
} TextObj;

#endif