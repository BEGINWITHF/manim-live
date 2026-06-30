#include "../draw_common.h"
#include "../shared_types.h"
#include <math.h>
#include <string.h>
#include <stdio.h>

#define MAX_BEZIER_PATHS 512
#define MAX_BEZIER_SEGMENTS 1024
#define BEZIER_SAMPLES 64

typedef struct {
    float px[4];
    float py[4];
} CubicSeg;

typedef struct {
    CubicSeg segs[MAX_BEZIER_SEGMENTS];
    int num_segs;
    int sr, sg, sb;
    float stroke_width;
    int fr, fg, fb;
    float fill_opacity;
    float progress;
    int show_stroke;
    int show_fill;
    int sub_count;
    int sub_seg_start[128];
    int sub_winding[128];
} BezierPathObj;

static BezierPathObj bezier_paths[MAX_BEZIER_PATHS];
static int bezier_path_count = 0;
static float g_fill_pts[MAX_BEZIER_SEGMENTS * BEZIER_SAMPLES + 1][2];

__declspec(dllexport) void AddBezierPath(
    const float *points, int num_points,
    int sr, int sg, int sb, float stroke_width,
    int fr, int fg, int fb, float fill_opacity,
    float progress, int show_stroke, int show_fill)
{
    if (bezier_path_count >= MAX_BEZIER_PATHS) return;
    if (num_points < 8) return;

    BezierPathObj *bp = &bezier_paths[bezier_path_count];
    int num_segs = num_points / 4;
    if (num_segs > MAX_BEZIER_SEGMENTS) num_segs = MAX_BEZIER_SEGMENTS;
    bp->num_segs = num_segs;
    bp->sr = sr; bp->sg = sg; bp->sb = sb;
    bp->stroke_width = stroke_width;
    bp->fr = fr; bp->fg = fg; bp->fb = fb;
    bp->fill_opacity = fill_opacity;
    bp->progress = progress;
    bp->show_stroke = show_stroke;
    bp->show_fill = show_fill;

    for (int i = 0; i < num_segs; i++) {
        int off = i * 4 * 3;
        for (int j = 0; j < 4; j++) {
            bp->segs[i].px[j] = points[off + j * 3 + 0];
            bp->segs[i].py[j] = points[off + j * 3 + 1];
        }
    }

    bp->sub_count = 1;
    bp->sub_seg_start[0] = 0;
    for (int si = 0; si < num_segs - 1; si++) {
        float dx = bp->segs[si].px[3] - bp->segs[si + 1].px[0];
        float dy = bp->segs[si].py[3] - bp->segs[si + 1].py[0];
        if (dx * dx + dy * dy > 40.0f) {
            if (bp->sub_count < 128) {
                bp->sub_seg_start[bp->sub_count++] = si + 1;
            }
        }
    }
    for (int s = 0; s < bp->sub_count; s++) {
        int start = bp->sub_seg_start[s];
        int end = (s < bp->sub_count - 1) ? bp->sub_seg_start[s + 1] : num_segs;
        float area = 0;
        for (int si = start; si < end; si++) {
            float x0 = bp->segs[si].px[0], y0 = bp->segs[si].py[0];
            float x3 = bp->segs[si].px[3], y3 = bp->segs[si].py[3];
            area += (x0 * y3 - x3 * y0);
        }
        bp->sub_winding[s] = (area >= 0) ? 1 : -1;
    }
    bezier_path_count++;
}

static void sample_cubic(const CubicSeg *s, float t, float *ox, float *oy) {
    float u = 1.0f - t;
    float u2 = u * u, u3 = u2 * u;
    float t2 = t * t, t3 = t2 * t;
    *ox = u3 * s->px[0] + 3.0f * u2 * t * s->px[1] + 3.0f * u * t2 * s->px[2] + t3 * s->px[3];
    *oy = u3 * s->py[0] + 3.0f * u2 * t * s->py[1] + 3.0f * u * t2 * s->py[2] + t3 * s->py[3];
}

static void tangent_cubic(const CubicSeg *s, float t, float *tx, float *ty) {
    float u = 1.0f - t;
    *tx = 3.0f * u * u * (s->px[1] - s->px[0]) +
          6.0f * u * t * (s->px[2] - s->px[1]) +
          3.0f * t * t * (s->px[3] - s->px[2]);
    *ty = 3.0f * u * u * (s->py[1] - s->py[0]) +
          6.0f * u * t * (s->py[2] - s->py[1]) +
          3.0f * t * t * (s->py[3] - s->py[2]);
}

static void tessellate_stroke(BezierPathObj *bp) {
    float nr = bp->sr / 255.0f;
    float ng = bp->sg / 255.0f;
    float nb = bp->sb / 255.0f;
    float half_w = bp->stroke_width * 0.5f + 0.5f;

    int total_segs = bp->num_segs;
    float progress = bp->progress;
    if (progress > 1.0f) progress = 1.0f;
    if (progress < 0.0f) progress = 0.0f;

    float target = progress * (float)total_segs;
    int full_segs = (int)target;
    float partial_t = target - (float)full_segs;
    if (full_segs > total_segs) full_segs = total_segs;

    float prev_x = 0, prev_y = 0, prev_nx = 0, prev_ny = 0;
    int has_prev = 0;

    int cur_sub = 0;
    float wind = (bp->sub_count > 0) ? (float)bp->sub_winding[0] : 1.0f;

    if (total_segs > 0 && full_segs >= 0) {
        const CubicSeg *s0 = &bp->segs[0];
        float tx0, ty0;
        sample_cubic(s0, 0.0f, &prev_x, &prev_y);
        tangent_cubic(s0, 0.0f, &tx0, &ty0);
        float tlen0 = sqrtf(tx0 * tx0 + ty0 * ty0);
        if (tlen0 < 0.0001f) tlen0 = 0.0001f;
        prev_nx = (-ty0 / tlen0) * half_w * wind;
        prev_ny = (tx0 / tlen0) * half_w * wind;
        has_prev = 1;
    }

    for (int si = 0; si <= full_segs && si < total_segs; si++) {
        const CubicSeg *s = &bp->segs[si];
        int n = BEZIER_SAMPLES;
        int end_n = (si == full_segs && partial_t > 0.001f) ? (int)(partial_t * n + 0.5f) : n;
        if (end_n < 1) end_n = 1;
        int start_i = (si == 0) ? 1 : 0;

        for (int i = start_i; i <= end_n; i++) {
            float t = (float)i / (float)n;
            if (si == full_segs && partial_t > 0.001f) {
                t = (float)i / (float)n * partial_t;
            }

            float px, py, tx, ty;
            sample_cubic(s, t, &px, &py);
            tangent_cubic(s, t, &tx, &ty);

            float tlen = sqrtf(tx * tx + ty * ty);
            if (tlen < 0.0001f) tlen = 0.0001f;

            if (si > 0 && i == start_i && has_prev) {
                float dx = px - prev_x;
                float dy = py - prev_y;
                if (dx * dx + dy * dy > 1600.0f) {
                    cur_sub++;
                    if (cur_sub < bp->sub_count) {
                        wind = (float)bp->sub_winding[cur_sub];
                    }
                    prev_x = px; prev_y = py;
                    prev_nx = (-ty / tlen) * half_w * wind;
                    prev_ny = (tx / tlen) * half_w * wind;
                    has_prev = 1;
                    continue;
                }
                float cnx = (-ty / tlen) * half_w * wind;
                float cny = (tx / tlen) * half_w * wind;
                if (g_vertex_count + 3 > MAX_VERTICES) return;
                PushVertex(prev_x, prev_y, nr, ng, nb);
                PushVertex(prev_x - prev_nx, prev_y - prev_ny, nr, ng, nb);
                PushVertex(px - cnx, py - cny, nr, ng, nb);
                prev_x = px; prev_y = py;
                prev_nx = cnx; prev_ny = cny;
                has_prev = 1;
                continue;
            }

            float nx = (-ty / tlen) * half_w * wind;
            float ny = (tx / tlen) * half_w * wind;

            if (has_prev) {
                if (g_vertex_count + 6 > MAX_VERTICES) return;
                PushVertex(prev_x, prev_y, nr, ng, nb);
                PushVertex(prev_x - prev_nx, prev_y - prev_ny, nr, ng, nb);
                PushVertex(px, py, nr, ng, nb);

                PushVertex(prev_x - prev_nx, prev_y - prev_ny, nr, ng, nb);
                PushVertex(px - nx, py - ny, nr, ng, nb);
                PushVertex(px, py, nr, ng, nb);
            }

            prev_x = px; prev_y = py;
            prev_nx = nx; prev_ny = ny;
            has_prev = 1;
        }
    }
}

static float g_cross_x[4096];
static int g_cross_dir[4096];

static int g_pt_sub[ MAX_BEZIER_SEGMENTS * BEZIER_SAMPLES + 1 ];

static void tessellate_fill(BezierPathObj *bp) {
    float fr = bp->fr / 255.0f;
    float fg = bp->fg / 255.0f;
    float fb = bp->fb / 255.0f;
    float fo = bp->fill_opacity;
    float cr = fr * fo, cg = fg * fo, cb = fb * fo;

    int total_pts = 0;

    for (int s = 0; s < bp->sub_count; s++) {
        int start = bp->sub_seg_start[s];
        int end = (s < bp->sub_count - 1) ? bp->sub_seg_start[s + 1] : bp->num_segs;

        int sub_start = total_pts;
        for (int si = start; si < end; si++) {
            const CubicSeg *seg = &bp->segs[si];
            for (int i = 0; i < BEZIER_SAMPLES; i++) {
                float t = (float)i / (float)BEZIER_SAMPLES;
                sample_cubic(seg, t, &g_fill_pts[total_pts][0], &g_fill_pts[total_pts][1]);
                g_pt_sub[total_pts] = s;
                total_pts++;
                if (total_pts >= MAX_BEZIER_SEGMENTS * BEZIER_SAMPLES) goto done_sample_all;
            }
        }
    }
done_sample_all:
    if (total_pts < 3) return;

    float y_min = g_fill_pts[0][1], y_max = g_fill_pts[0][1];
    for (int i = 1; i < total_pts; i++) {
        if (g_fill_pts[i][1] < y_min) y_min = g_fill_pts[i][1];
        if (g_fill_pts[i][1] > y_max) y_max = g_fill_pts[i][1];
    }

    int y_start = (int)floorf(y_min);
    int y_end = (int)ceilf(y_max);

    for (int y = y_start; y <= y_end; y++) {
        float scan_y = (float)y + 0.5f;
        int n_cross = 0;

        for (int i = 0; i < total_pts && n_cross < 4096; i++) {
            int j;
            if (i + 1 < total_pts && g_pt_sub[i] == g_pt_sub[i + 1]) {
                j = i + 1;
            } else {
                int s = g_pt_sub[i];
                int sub_seg_end = (s < bp->sub_count - 1) ? bp->sub_seg_start[s + 1] : bp->num_segs;
                int sub_start_idx = 0;
                for (int k = 0; k < total_pts; k++) {
                    if (g_pt_sub[k] == s) { sub_start_idx = k; break; }
                }
                j = sub_start_idx;
            }
            float yi = g_fill_pts[i][1];
            float yj = g_fill_pts[j][1];
            float dy = yj - yi;
            if (fabsf(dy) < 0.0001f) continue;
            float ey0 = yi, ey1 = yj;
            if (ey0 > ey1) { float tmp = ey0; ey0 = ey1; ey1 = tmp; }
            if (scan_y <= ey0 || scan_y > ey1) continue;
            float t = (scan_y - yi) / dy;
            g_cross_x[n_cross] = g_fill_pts[i][0] + t * (g_fill_pts[j][0] - g_fill_pts[i][0]);
            g_cross_dir[n_cross] = (dy > 0) ? 1 : -1;
            n_cross++;
        }

        for (int a = 1; a < n_cross; a++) {
            float key_x = g_cross_x[a];
            int key_d = g_cross_dir[a];
            int b = a - 1;
            while (b >= 0 && g_cross_x[b] > key_x) {
                g_cross_x[b + 1] = g_cross_x[b];
                g_cross_dir[b + 1] = g_cross_dir[b];
                b--;
            }
            g_cross_x[b + 1] = key_x;
            g_cross_dir[b + 1] = key_d;
        }

        int inside = 0;
        for (int i = 0; i < n_cross; i++) {
            inside ^= 1;
            if (inside && i + 1 < n_cross) {
                float xl = g_cross_x[i];
                float xr = g_cross_x[i + 1];
                if (xr <= xl) continue;

                int px_start = (int)floorf(xl);
                int px_end = (int)ceilf(xr);

                for (int px = px_start; px < px_end; px++) {
                    float seg_l = (float)px;
                    float seg_r = (float)px + 1.0f;
                    float coverage_l = (xl > seg_l) ? xl : seg_l;
                    float coverage_r = (xr < seg_r) ? xr : seg_r;
                    float coverage = coverage_r - coverage_l;
                    if (coverage < 0.05f) continue;

                    float a_r = cr * coverage;
                    float a_g = cg * coverage;
                    float a_b = cb * coverage;
                    if (g_vertex_count + 6 > MAX_VERTICES) return;
                    PushVertex(seg_l, scan_y, a_r, a_g, a_b);
                    PushVertex(seg_r, scan_y, a_r, a_g, a_b);
                    PushVertex(seg_r, scan_y + 1.0f, a_r, a_g, a_b);

                    PushVertex(seg_l, scan_y, a_r, a_g, a_b);
                    PushVertex(seg_r, scan_y + 1.0f, a_r, a_g, a_b);
                    PushVertex(seg_l, scan_y + 1.0f, a_r, a_g, a_b);
                }
            }
        }
    }
}

void BuildVerticesFromBezierPaths(void) {
    for (int i = 0; i < bezier_path_count; i++) {
        BezierPathObj *bp = &bezier_paths[i];
        if (bp->show_fill && bp->fill_opacity > 0.001f) {
            tessellate_fill(bp);
        }
        if (bp->show_stroke && bp->stroke_width > 0.001f) {
            tessellate_stroke(bp);
        }
    }
    bezier_path_count = 0;
}
