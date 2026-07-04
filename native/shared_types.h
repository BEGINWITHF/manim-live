#ifndef SHARED_TYPES_H
#define SHARED_TYPES_H

#ifndef MAX_SHAPES
#define MAX_SHAPES 4096
#endif

#ifndef MAX_POLYGON_VERTS
#define MAX_POLYGON_VERTS 64
#endif

typedef struct {
    float x, y, hw, hh, rot;
    int r, g, b;
    float alpha;
} Rect;

typedef struct {
    float x, y, radius;
    int r, g, b;
    int border_r, border_g, border_b;
    float border_width;
    float stroke_progress;
    float alpha;
} Circle;

typedef struct {
    float x1, y1, x2, y2;
    int width, r, g, b;
    float alpha;
} LineObj;

typedef struct {
    float x, y, rx, ry;
    int r, g, b;
    float alpha;
} EllipseObj;

typedef struct {
    float x, y;
    int r, g, b;
    int border_r, border_g, border_b;
    float border_width;
    int vert_count;
    float verts[MAX_POLYGON_VERTS * 2];
    float alpha;
} PolygonObj;

typedef struct {
    float x1, y1, x2, y2;
    int width, r, g, b;
    float dash_length;
    float gap_length;
    float alpha;
} DashedLineObj;

typedef struct {
    float x, y, radius;
    float start_angle, angle;
    int r, g, b;
    float stroke_width;
    float alpha;
} ArcObj;

typedef struct {
    float x, y;
    int r, g, b;
    float alpha;
} PointObj;

#ifndef MAX_TEXT_LEN
#define MAX_TEXT_LEN 512
#endif

typedef struct {
    float x, y;
    int r, g, b;
    float font_size;
    float opacity;
    char text[MAX_TEXT_LEN];
    float alpha;
} TextObj;

#endif