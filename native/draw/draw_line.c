#include "../draw_common.h"

void BuildVerticesFromLines(const LineObj *lines, int count) {
    for (int i = 0; i < count; i++) {
        if (g_vertex_count + 6 > MAX_VERTICES) break;

        const LineObj *l = &lines[i];
        float nr = l->r / 255.0f, ng = l->g / 255.0f, nb = l->b / 255.0f;

        float dx = l->x2 - l->x1;
        float dy = l->y2 - l->y1;
        float len = sqrtf(dx*dx + dy*dy);

        if (len < 0.0001f) continue;

        float thick = (float)l->width;
        float half_thick = thick * 0.5f + 0.5f;
        float nx = (-dy / len) * half_thick;
        float ny = (dx / len) * half_thick;

        float ux = dx / len;
        float uy = dy / len;
        float ex1 = l->x1 - ux * half_thick;
        float ey1 = l->y1 - uy * half_thick;
        float ex2 = l->x2 + ux * half_thick;
        float ey2 = l->y2 + uy * half_thick;

        PushVertex(ex1 + nx, ey1 + ny, nr, ng, nb, l->alpha);
        PushVertex(ex1 - nx, ey1 - ny, nr, ng, nb, l->alpha);
        PushVertex(ex2 + nx, ey2 + ny, nr, ng, nb, l->alpha);

        PushVertex(ex1 - nx, ey1 - ny, nr, ng, nb, l->alpha);
        PushVertex(ex2 - nx, ey2 - ny, nr, ng, nb, l->alpha);
        PushVertex(ex2 + nx, ey2 + ny, nr, ng, nb, l->alpha);
    }
}