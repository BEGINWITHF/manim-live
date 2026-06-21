#define STB_TRUETYPE_IMPLEMENTATION
#include "../stb_truetype.h"
#include "../draw_common.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_FONTS 4

static unsigned char font_data[MAX_FONTS][1 << 25];
static stbtt_fontinfo fonts[MAX_FONTS];
static int font_count = 0;

static int utf8_decode(const char *text, int *ci, int *codepoint) {
    unsigned char c = (unsigned char)text[*ci];
    if (c < 0x80) {
        *codepoint = c;
        (*ci)++;
        return 1;
    } else if ((c & 0xE0) == 0xC0) {
        unsigned char c2 = (unsigned char)text[*ci + 1];
        *codepoint = ((c & 0x1F) << 6) | (c2 & 0x3F);
        (*ci) += 2;
        return 2;
    } else if ((c & 0xF0) == 0xE0) {
        unsigned char c2 = (unsigned char)text[*ci + 1];
        unsigned char c3 = (unsigned char)text[*ci + 2];
        *codepoint = ((c & 0x0F) << 12) | ((c2 & 0x3F) << 6) | (c3 & 0x3F);
        (*ci) += 3;
        return 3;
    } else if ((c & 0xF8) == 0xF0) {
        unsigned char c2 = (unsigned char)text[*ci + 1];
        unsigned char c3 = (unsigned char)text[*ci + 2];
        unsigned char c4 = (unsigned char)text[*ci + 3];
        *codepoint = ((c & 0x07) << 18) | ((c2 & 0x3F) << 12) | ((c3 & 0x3F) << 6) | (c4 & 0x3F);
        (*ci) += 4;
        return 4;
    }
    *codepoint = 0;
    (*ci)++;
    return 1;
}

__declspec(dllexport) int Text_LoadFont(const unsigned char *data, int data_len) {
    if (font_count >= MAX_FONTS) return 0;
    if (data_len <= 0 || data_len > (int)sizeof(font_data[font_count])) return 0;

    memcpy(font_data[font_count], data, data_len);
    memset(&fonts[font_count], 0, sizeof(stbtt_fontinfo));
    int offset = stbtt_GetFontOffsetForIndex(font_data[font_count], 0);
    if (offset < 0) return 0;
    if (stbtt_InitFont(&fonts[font_count], font_data[font_count], offset)) {
        font_count++;
        return 1;
    }
    return 0;
}

static int pick_best_font(const char *text) {
    int best = 0;
    int best_score = -1;
    for (int f = 0; f < font_count; f++) {
        int score = 0;
        int ci = 0;
        int len = (int)strlen(text);
        while (ci < len) {
            int cp;
            utf8_decode(text, &ci, &cp);
            if (cp < 32) continue;
            int idx = stbtt_FindGlyphIndex(&fonts[f], cp);
            if (idx != 0) score++;
        }
        if (score > best_score) {
            best_score = score;
            best = f;
        }
    }
    return best;
}

static int get_glyph_font(int codepoint) {
    int first_font = -1;
    for (int f = 0; f < font_count; f++) {
        int idx = stbtt_FindGlyphIndex(&fonts[f], codepoint);
        if (idx != 0) {
            if (first_font < 0) first_font = f;
        }
    }
    return first_font >= 0 ? first_font : 0;
}

void BuildVerticesFromTexts(const TextObj *texts, int count) {
    if (font_count == 0) return;

    for (int i = 0; i < count; i++) {
        const TextObj *t = &texts[i];
        if (t->text[0] == '\0') continue;

        float r = t->r / 255.0f;
        float g = t->g / 255.0f;
        float b = t->b / 255.0f;

        int best = pick_best_font(t->text);
        float scale = stbtt_ScaleForPixelHeight(&fonts[best], t->font_size);

        int len = (int)strlen(t->text);
        float text_width = 0;

        int ci = 0;
        while (ci < len) {
            int cp;
            utf8_decode(t->text, &ci, &cp);
            int adv = 0;
            stbtt_GetCodepointHMetrics(&fonts[best], cp, &adv, NULL);
            if (adv == 0) {
                stbtt_GetCodepointHMetrics(&fonts[0], cp, &adv, NULL);
            }
            if (cp == 32 && adv == 0) {
                stbtt_GetCodepointHMetrics(&fonts[best], 'x', &adv, NULL);
                if (adv == 0) adv = 1024;
            }
            text_width += adv * scale;
        }

        float cursor_x = t->x - text_width * 0.5f;
        float baseline_y = t->y;

        ci = 0;
        while (ci < len) {
            int cp;
            utf8_decode(t->text, &ci, &cp);
            if (cp < 32) continue;

            int fi = best;
            int idx = stbtt_FindGlyphIndex(&fonts[best], cp);
            if (idx == 0) fi = get_glyph_font(cp);
            float fscale = stbtt_ScaleForPixelHeight(&fonts[fi], t->font_size);

            int adv = 0;
            stbtt_GetCodepointHMetrics(&fonts[best], cp, &adv, NULL);
            if (adv == 0) {
                stbtt_GetCodepointHMetrics(&fonts[0], cp, &adv, NULL);
            }
            if (cp == 32 && adv == 0) {
                stbtt_GetCodepointHMetrics(&fonts[best], 'x', &adv, NULL);
                if (adv == 0) adv = 1024;
            }

            int w = 0, h = 0, xoff = 0, yoff = 0;
            unsigned char *bmp = stbtt_GetCodepointBitmap(&fonts[fi], fscale, fscale, cp, &w, &h, &xoff, &yoff);

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

            cursor_x += adv * scale;
        }
    }
}
