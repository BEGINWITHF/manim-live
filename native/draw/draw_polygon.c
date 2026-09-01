#include <math.h>
#include "../draw_common.h"

void BuildVerticesFromPolygons(const PolygonObj* polygons, int count) {
    for (int i = 0; i < count; i++) {
        const PolygonObj* p = &polygons[i];
        int n = p->vert_count;
        if (n < 3) continue;

        float fill_r = p->r / 255.0f, fill_g = p->g / 255.0f, fill_b = p->b / 255.0f;
        float br = p->border_r / 255.0f, bg = p->border_g / 255.0f, bb = p->border_b / 255.0f;

        float sp = p->stroke_progress;
        if (sp > 1.0f) sp = 1.0f;
        if (sp < 0.0f) sp = 0.0f;

        float edge_lens[64];
        float perimeter = 0.0f;
        for (int j = 0; j < n; j++) {
            int j2 = (j + 1) % n;
            float dx = p->verts[j2 * 2] - p->verts[j * 2];
            float dy = p->verts[j2 * 2 + 1] - p->verts[j * 2 + 1];
            edge_lens[j] = sqrtf(dx * dx + dy * dy);
            perimeter += edge_lens[j];
        }

        float drawn = perimeter * sp;

        /* Fill: triangle fan from polygon CENTROID (not first vertex).
           A fan from vertex 0 fills self-intersecting/concave shapes (e.g.
           a 5-pointed Star, which has alternating outer/inner vertices)
           incorrectly — it fills the concavities between points. Fanning
           from the centroid tiles any star-shaped polygon correctly. */
        if (p->r != 0 || p->g != 0 || p->b != 0) {
            float cx = 0.0f, cy = 0.0f;
            for (int j = 0; j < n; j++) { cx += p->verts[j * 2]; cy += p->verts[j * 2 + 1]; }
            cx /= (float)n;
            cy /= (float)n;
            float fan_x = cx;
            float fan_y = cy;
            float cum = 0.0f;
            for (int j = 0; j < n; j++) {
                int j2 = (j + 1) % n;
                float el = edge_lens[j];
                if (cum >= drawn) break;

                float x0 = p->verts[j * 2], y0 = p->verts[j * 2 + 1];
                float x1, y1;

                if (cum + el <= drawn) {
                    x1 = p->verts[j2 * 2];
                    y1 = p->verts[j2 * 2 + 1];
                    cum += el;
                } else {
                    float frac = (drawn - cum) / el;
                    x1 = x0 + (p->verts[j2 * 2] - x0) * frac;
                    y1 = y0 + (p->verts[j2 * 2 + 1] - y0) * frac;
                    cum = drawn;
                }

                if (g_vertex_count + 3 > MAX_VERTICES) break;
                PushVertex(fan_x, fan_y, fill_r, fill_g, fill_b, p->alpha);
                PushVertex(x0, y0, fill_r, fill_g, fill_b, p->alpha);
                PushVertex(x1, y1, fill_r, fill_g, fill_b, p->alpha);
            }
        }

        /* Border: progressive line segments */
        if (p->border_width > 0.0f) {
            float cum = 0.0f;
            for (int j = 0; j < n; j++) {
                if (cum >= drawn) break;
                int j2 = (j + 1) % n;
                float el = edge_lens[j];

                float x0 = p->verts[j * 2], y0 = p->verts[j * 2 + 1];
                float ex, ey;

                if (cum + el <= drawn) {
                    ex = p->verts[j2 * 2];
                    ey = p->verts[j2 * 2 + 1];
                    cum += el;
                } else {
                    float frac = (drawn - cum) / el;
                    ex = x0 + (p->verts[j2 * 2] - x0) * frac;
                    ey = y0 + (p->verts[j2 * 2 + 1] - y0) * frac;
                    cum = drawn;
                }

                float dx = ex - x0, dy = ey - y0;
                float len = sqrtf(dx * dx + dy * dy);
                if (len < 0.0001f) continue;
                float hw = p->border_width * 0.5f;
                float nx = (-dy / len) * hw;
                float ny = (dx / len) * hw;

                if (g_vertex_count + 6 > MAX_VERTICES) break;
                PushVertex(x0 + nx, y0 + ny, br, bg, bb, p->alpha);
                PushVertex(x0 - nx, y0 - ny, br, bg, bb, p->alpha);
                PushVertex(ex + nx, ey + ny, br, bg, bb, p->alpha);

                PushVertex(x0 - nx, y0 - ny, br, bg, bb, p->alpha);
                PushVertex(ex - nx, ey - ny, br, bg, bb, p->alpha);
                PushVertex(ex + nx, ey + ny, br, bg, bb, p->alpha);
            }
        }
    }
}
