#include "../draw_common.h"

void BuildVerticesFromRects(const Rect *rects, int count) {
    for (int i = 0; i < count; i++) {
        if (g_vertex_count + 6 > MAX_VERTICES) break;

        const Rect *r = &rects[i];
        float nr = r->r / 255.0f, ng = r->g / 255.0f, nb = r->b / 255.0f;

        float hw = r->hw, hh = r->hh;
        float cos_a = cosf(r->rot), sin_a = sinf(r->rot);

        float corners[4][2] = {{-hw,-hh},{hw,-hh},{hw,hh},{-hw,hh}};
        float rot[4][2];

        for (int j = 0; j < 4; j++) {
            rot[j][0] = r->x + corners[j][0]*cos_a - corners[j][1]*sin_a;
            rot[j][1] = r->y + corners[j][0]*sin_a + corners[j][1]*cos_a;
        }

        PushVertex(rot[0][0], rot[0][1], nr, ng, nb);
        PushVertex(rot[1][0], rot[1][1], nr, ng, nb);
        PushVertex(rot[2][0], rot[2][1], nr, ng, nb);

        PushVertex(rot[0][0], rot[0][1], nr, ng, nb);
        PushVertex(rot[2][0], rot[2][1], nr, ng, nb);
        PushVertex(rot[3][0], rot[3][1], nr, ng, nb);
    }
}