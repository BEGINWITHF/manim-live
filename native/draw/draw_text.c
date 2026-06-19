#define STB_TRUETYPE_IMPLEMENTATION
#include "../stb_truetype.h"
#include "../draw_common.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

static unsigned char font_data[1 << 20];
static stbtt_fontinfo font;
static int font_ok = 0;

__declspec(dllexport) int Text_LoadFont(const unsigned char *data, int data_len) {
    if (data_len <= 0 || data_len > (int)sizeof(font_data)) return 0;
    memcpy(font_data, data, data_len);
    memset(&font, 0, sizeof(font));
    int offset = stbtt_GetFontOffsetForIndex(font_data, 0);
    if (offset < 0) return 0;
    if (stbtt_InitFont(&font, font_data, offset)) {
        font_ok = 1;
        return 1;
    }
    return 0;
}

void BuildVerticesFromTexts(const TextObj *texts, int count) {
    if (!font_ok) return;

    for (int i = 0; i < count; i++) {
        const TextObj *t = &texts[i];
        if (t->text[0] == '\0') continue;

        float r = t->r / 255.0f;
        float g = t->g / 255.0f;
        float b = t->b / 255.0f;

        float scale = stbtt_ScaleForPixelHeight(&font, t->font_size);

        int len = (int)strlen(t->text);
        float text_width = 0;
        for (int ci = 0; ci < len; ci++) {
            int adv;
            stbtt_GetCodepointHMetrics(&font, (unsigned char)t->text[ci], &adv, NULL);
            text_width += adv * scale;
        }

        float cursor_x = t->x - text_width * 0.5f;
        float baseline_y = t->y;

        for (int ci = 0; ci < len; ci++) {
            unsigned char ch = (unsigned char)t->text[ci];
            if (ch < 32) continue;

            int advance;
            stbtt_GetCodepointHMetrics(&font, ch, &advance, NULL);

            int w = 0, h = 0, xoff = 0, yoff = 0;
            unsigned char *bmp = stbtt_GetCodepointBitmap(&font, scale, scale, ch, &w, &h, &xoff, &yoff);

            if (bmp && w > 0 && h > 0) {
                float glyph_left = cursor_x + (float)xoff;
                float glyph_top  = baseline_y + (float)yoff;

                for (int row = 0; row < h; row++) {
                    int col = 0;
                    while (col < w) {
                        if (bmp[row * w + col] > 0) {
                            int run_start = col;
                            while (col < w && bmp[row * w + col] > 0) col++;
                            int run_end = col;

                            float x0 = glyph_left + (float)run_start;
                            float y0 = glyph_top  + (float)row;
                            float x1 = glyph_left + (float)run_end;
                            float y1 = y0 + 1.0f;

                            PushVertex(x0, y0, r, g, b);
                            PushVertex(x1, y0, r, g, b);
                            PushVertex(x1, y1, r, g, b);
                            PushVertex(x0, y0, r, g, b);
                            PushVertex(x1, y1, r, g, b);
                            PushVertex(x0, y1, r, g, b);
                        } else {
                            col++;
                        }
                    }
                }
                stbtt_FreeBitmap(bmp, NULL);
            }

            cursor_x += advance * scale;
        }
    }
}
