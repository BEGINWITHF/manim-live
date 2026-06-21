#include <math.h>
#include "../draw_common.h"

void BuildVerticesFromEllipses(const EllipseObj* ellipses, int count) {
    const int segs = 36;
    for (int i = 0; i < count; i++) {
        const EllipseObj* e = &ellipses[i];
        float nr = e->r / 255.0f, ng = e->g / 255.0f, nb = e->b / 255.0f;

        if (g_vertex_count + segs * 3 > MAX_VERTICES) break;

        for (int j = 0; j < segs; j++) {
            float a1 = 2.0f * 3.14159265f * j / segs;
            float a2 = 2.0f * 3.14159265f * (j + 1) / segs;

            float x1 = e->x + cosf(a1) * e->rx;
            float y1 = e->y + sinf(a1) * e->ry;
            float x2 = e->x + cosf(a2) * e->rx;
            float y2 = e->y + sinf(a2) * e->ry;

            PushVertex(e->x, e->y, nr, ng, nb);
            PushVertex(x1, y1, nr, ng, nb);
            PushVertex(x2, y2, nr, ng, nb);
        }
    }
}
