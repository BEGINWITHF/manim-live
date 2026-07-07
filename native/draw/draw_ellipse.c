#include <math.h>
#include "../draw_common.h"

void BuildVerticesFromEllipses(const EllipseObj *ellipses, int count) {
    const int segs = 48;

    for (int i = 0; i < count; i++) {
        const EllipseObj *e = &ellipses[i];

        float nr = e->r / 255.0f, ng = e->g / 255.0f, nb = e->b / 255.0f;
        float bn = e->border_r / 255.0f, bg = e->border_g / 255.0f, bb = e->border_b / 255.0f;

        float sp = e->stroke_progress;
        if (sp > 1.0f) sp = 1.0f;
        if (sp < 0.0f) sp = 0.0f;

        int fill_segs = (int)(segs * sp);
        if (fill_segs > segs) fill_segs = segs;
        if (fill_segs < 1) fill_segs = 1;

        if (g_vertex_count + (fill_segs * 3) > MAX_VERTICES) break;

        float start_x = e->x + e->rx;
        float start_y = e->y;

        for (int j = 0; j < fill_segs; j++) {
            float a1 = -2.0f * 3.14159265f * (float)j / (float)segs;
            float a2 = -2.0f * 3.14159265f * (float)(j + 1) / (float)segs;

            float x1 = e->x + cosf(a1) * e->rx;
            float y1 = e->y + sinf(a1) * e->ry;
            float x2 = e->x + cosf(a2) * e->rx;
            float y2 = e->y + sinf(a2) * e->ry;

            PushVertex(start_x, start_y, nr, ng, nb, e->alpha);
            PushVertex(x1, y1, nr, ng, nb, e->alpha);
            PushVertex(x2, y2, nr, ng, nb, e->alpha);
        }

        if (e->border_width > 0.0f && sp > 0.0f) {
            int draw_segs = fill_segs;
            if (g_vertex_count + (draw_segs * 6) > MAX_VERTICES) break;

            float inner_r_x = e->rx - e->border_width;
            float inner_r_y = e->ry - e->border_width;
            if (inner_r_x < 0.0f) inner_r_x = 0.0f;
            if (inner_r_y < 0.0f) inner_r_y = 0.0f;

            for (int j = 0; j < draw_segs; j++) {
                float a1 = -2.0f * 3.14159265f * (float)j / (float)segs;
                float a2 = -2.0f * 3.14159265f * (float)(j + 1) / (float)segs;

                PushVertex(e->x + cosf(a1) * inner_r_x, e->y + sinf(a1) * inner_r_y, bn, bg, bb, e->alpha);
                PushVertex(e->x + cosf(a1) * e->rx, e->y + sinf(a1) * e->ry, bn, bg, bb, e->alpha);
                PushVertex(e->x + cosf(a2) * inner_r_x, e->y + sinf(a2) * inner_r_y, bn, bg, bb, e->alpha);

                PushVertex(e->x + cosf(a1) * e->rx, e->y + sinf(a1) * e->ry, bn, bg, bb, e->alpha);
                PushVertex(e->x + cosf(a2) * e->rx, e->y + sinf(a2) * e->ry, bn, bg, bb, e->alpha);
                PushVertex(e->x + cosf(a2) * inner_r_x, e->y + sinf(a2) * inner_r_y, bn, bg, bb, e->alpha);
            }
        }
    }
}
