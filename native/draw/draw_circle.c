#include "../draw_common.h"

void BuildVerticesFromCircles(const Circle *circles, int count) {
    const int segs = 36;

    for (int i = 0; i < count; i++) {
        if (g_vertex_count + (segs * 3) > MAX_VERTICES) break;

        const Circle *c = &circles[i];

        float nr = c->r / 255.0f, ng = c->g / 255.0f, nb = c->b / 255.0f;
        float step = 2.0f * 3.14159265f / (float)segs;

        for (int j = 0; j < segs; j++) {
            float a1 = step * (float)j;
            float a2 = step * (float)(j + 1);

            PushVertex(c->x, c->y, nr, ng, nb);
            PushVertex(c->x + cosf(a1)*c->radius, c->y + sinf(a1)*c->radius, nr, ng, nb);
            PushVertex(c->x + cosf(a2)*c->radius, c->y + sinf(a2)*c->radius, nr, ng, nb);
        }
    }
}