#include <math.h>
#include "../draw_common.h"

void BuildVerticesFromPolygons(const PolygonObj* polygons, int count) {
    for (int i = 0; i < count; i++) {
        const PolygonObj* p = &polygons[i];
        int n = p->vert_count;
        if (n < 3) continue;

        float fr = p->border_r / 255.0f, fg = p->border_g / 255.0f, fb = p->border_b / 255.0f;
        float fill_r = p->r / 255.0f, fill_g = p->g / 255.0f, fill_b = p->b / 255.0f;

        /* Outline: n line segments as thin quads */
        if (p->border_width > 0.0f) {
            if (g_vertex_count + n * 6 > MAX_VERTICES) break;
            for (int j = 0; j < n; j++) {
                int j2 = (j + 1) % n;
                float x1 = p->verts[j * 2];
                float y1 = p->verts[j * 2 + 1];
                float x2 = p->verts[j2 * 2];
                float y2 = p->verts[j2 * 2 + 1];

                float dx = x2 - x1;
                float dy = y2 - y1;
                float len = sqrtf(dx * dx + dy * dy);
                if (len < 0.0001f) continue;
                float hw = p->border_width * 0.5f;
                float nx = (-dy / len) * hw;
                float ny = (dx / len) * hw;

                PushVertex(x1 + nx, y1 + ny, fr, fg, fb);
                PushVertex(x1 - nx, y1 - ny, fr, fg, fb);
                PushVertex(x2 + nx, y2 + ny, fr, fg, fb);

                PushVertex(x1 - nx, y1 - ny, fr, fg, fb);
                PushVertex(x2 - nx, y2 - ny, fr, fg, fb);
                PushVertex(x2 + nx, y2 + ny, fr, fg, fb);
            }
        }

        /* Fill: triangle fan from centroid */
        if (g_vertex_count + n * 3 > MAX_VERTICES) break;
        for (int j = 0; j < n; j++) {
            int j2 = (j + 1) % n;
            PushVertex(p->x, p->y, fill_r, fill_g, fill_b);
            PushVertex(p->verts[j * 2], p->verts[j * 2 + 1], fill_r, fill_g, fill_b);
            PushVertex(p->verts[j2 * 2], p->verts[j2 * 2 + 1], fill_r, fill_g, fill_b);
        }
    }
}
