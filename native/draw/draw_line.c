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
        float nx = (-dy / len) * (thick * 0.5f);
        float ny = (dx / len) * (thick * 0.5f);

        PushVertex(l->x1 + nx, l->y1 + ny, nr, ng, nb);
        PushVertex(l->x1 - nx, l->y1 - ny, nr, ng, nb);
        PushVertex(l->x2 + nx, l->y2 + ny, nr, ng, nb);

        PushVertex(l->x1 - nx, l->y1 - ny, nr, ng, nb);
        PushVertex(l->x2 - nx, l->y2 - ny, nr, ng, nb);
        PushVertex(l->x2 + nx, l->y2 + ny, nr, ng, nb);
    }
}