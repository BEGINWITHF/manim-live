#include <windows.h>
#include "../draw_common.h"
#include <string.h>
#include <stdlib.h>

static HDC g_gdi_hdc = NULL;

__declspec(dllexport) int Text_LoadFont(const unsigned char *data, int data_len) {
    (void)data; (void)data_len;
    return 1;
}

void GDI_Text_Init(void) {
    if (!g_gdi_hdc)
        g_gdi_hdc = CreateCompatibleDC(NULL);
}

void GDI_Text_Shutdown(void) {
    if (g_gdi_hdc) { DeleteDC(g_gdi_hdc); g_gdi_hdc = NULL; }
}

static int gdi_utf8_decode(const char *text, int *ci, int *codepoint) {
    unsigned char c = (unsigned char)text[*ci];
    if (c < 0x80) { *codepoint = c; (*ci)++; return 1; }
    if ((c & 0xE0) == 0xC0) {
        *codepoint = ((c & 0x1F) << 6) | ((unsigned char)text[*ci+1] & 0x3F);
        (*ci) += 2; return 2;
    }
    if ((c & 0xF0) == 0xE0) {
        *codepoint = ((c & 0x0F) << 12) | (((unsigned char)text[*ci+1] & 0x3F) << 6) | ((unsigned char)text[*ci+2] & 0x3F);
        (*ci) += 3; return 3;
    }
    if ((c & 0xF8) == 0xF0) {
        *codepoint = ((c & 0x07) << 18) | (((unsigned char)text[*ci+1] & 0x3F) << 12) |
                     (((unsigned char)text[*ci+2] & 0x3F) << 6) | ((unsigned char)text[*ci+3] & 0x3F);
        (*ci) += 4; return 4;
    }
    *codepoint = 0; (*ci)++; return 1;
}

static int gdi_encode_utf8(int cp, char *out) {
    if (cp < 0x80) { out[0] = (char)cp; return 1; }
    if (cp < 0x800) { out[0] = 0xC0 | (cp >> 6); out[1] = 0x80 | (cp & 0x3F); return 2; }
    out[0] = 0xE0 | (cp >> 12);
    out[1] = 0x80 | ((cp >> 6) & 0x3F);
    out[2] = 0x80 | (cp & 0x3F);
    return 3;
}

void BuildVerticesFromTexts(const TextObj *texts, int count) {
    if (!g_gdi_hdc) GDI_Text_Init();
    if (!g_gdi_hdc) return;

    for (int i = 0; i < count; i++) {
        const TextObj *t = &texts[i];
        if (t->text[0] == '\0') continue;

        float base_r = t->r / 255.0f;
        float base_g = t->g / 255.0f;
        float base_b = t->b / 255.0f;

        int font_size_px = (int)(t->font_size + 0.5f);
        if (font_size_px < 1) font_size_px = 1;

        const char *font_name = t->font_name[0] ? t->font_name : "Arial";
        HFONT font = CreateFontA(
            font_size_px, 0, 0, 0,
            FW_NORMAL, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE,
            font_name
        );
        HFONT old_font = (HFONT)SelectObject(g_gdi_hdc, font);

        int len = (int)strlen(t->text);

        int total_chars = 0;
        { int ci2 = 0; while (ci2 < len) { int cp2; gdi_utf8_decode(t->text, &ci2, &cp2); if (cp2 > 32 && cp2 != 10) total_chars++; } }

        float char_progress = t->opacity * (float)total_chars;
        int full_chars = (int)char_progress;
        float frac = char_progress - (float)full_chars;
        if (t->opacity >= 1.0f) { full_chars = total_chars; frac = 0.0f; }
        if (full_chars > total_chars) full_chars = total_chars;

        SIZE total_sz;
        GetTextExtentPoint32A(g_gdi_hdc, t->text, len, &total_sz);

        float cursor_x = t->x - total_sz.cx * 0.5f;
        float baseline_y = t->y - total_sz.cy * 0.5f;

        int visible_char_idx = 0;
        int ci = 0;
        while (ci < len) {
            int cp;
            gdi_utf8_decode(t->text, &ci, &cp);

            if (cp == 10) {
                cursor_x = t->x - total_sz.cx * 0.5f;
                baseline_y += t->font_size * 1.2f;
                continue;
            }
            if (cp < 32) continue;

            float char_alpha = 0.0f;
            if (visible_char_idx < full_chars) {
                char_alpha = 1.0f;
            } else if (visible_char_idx == full_chars && frac > 0.0f) {
                char_alpha = frac;
            } else if (t->opacity >= 1.0f) {
                char_alpha = 1.0f;
            }
            visible_char_idx++;

            char char_str[8] = {0};
            int char_len = gdi_encode_utf8(cp, char_str);

            SIZE char_sz;
            GetTextExtentPoint32A(g_gdi_hdc, char_str, char_len, &char_sz);

            if (char_alpha > 0.004f && char_sz.cx > 0 && char_sz.cy > 0) {
                BITMAPINFO bmi = {0};
                bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
                bmi.bmiHeader.biWidth = char_sz.cx;
                bmi.bmiHeader.biHeight = -char_sz.cy;
                bmi.bmiHeader.biPlanes = 1;
                bmi.bmiHeader.biBitCount = 32;
                bmi.bmiHeader.biCompression = BI_RGB;

                void *pixels = NULL;
                HBITMAP dib = CreateDIBSection(g_gdi_hdc, &bmi, DIB_RGB_COLORS, &pixels, NULL, 0);
                HBITMAP old_dib = (HBITMAP)SelectObject(g_gdi_hdc, dib);

                RECT rc = {0, 0, char_sz.cx, char_sz.cy};
                FillRect(g_gdi_hdc, &rc, (HBRUSH)GetStockObject(BLACK_BRUSH));

                SetBkMode(g_gdi_hdc, TRANSPARENT);
                SetTextColor(g_gdi_hdc, RGB(255, 255, 255));
                TextOutA(g_gdi_hdc, 0, 0, char_str, char_len);

                unsigned char *px = (unsigned char *)pixels;
                float cr = base_r * char_alpha;
                float cg = base_g * char_alpha;
                float cb = base_b * char_alpha;

                for (int row = 0; row < char_sz.cy; row++) {
                    int col = 0;
                    while (col < char_sz.cx) {
                        unsigned char br = px[(row * char_sz.cx + col) * 4 + 2];
                        unsigned char bg = px[(row * char_sz.cx + col) * 4 + 1];
                        unsigned char bb = px[(row * char_sz.cx + col) * 4 + 0];
                        if (br > 1 || bg > 1 || bb > 1) {
                            int run_start = col;
                            while (col < char_sz.cx) {
                                unsigned char rr = px[(row * char_sz.cx + col) * 4 + 2];
                                unsigned char gg = px[(row * char_sz.cx + col) * 4 + 1];
                                unsigned char bbb = px[(row * char_sz.cx + col) * 4 + 0];
                                if (rr <= 1 && gg <= 1 && bbb <= 1) break;
                                col++;
                            }
                            int run_end = col;

                            float x0 = cursor_x + (float)run_start;
                            float y0 = baseline_y + (float)row;
                            float x1 = cursor_x + (float)run_end;
                            float y1 = y0 + 1.0f;

                            PushVertex(x0, y0, cr, cg, cb, t->alpha);
                            PushVertex(x1, y0, cr, cg, cb, t->alpha);
                            PushVertex(x1, y1, cr, cg, cb, t->alpha);
                            PushVertex(x0, y0, cr, cg, cb, t->alpha);
                            PushVertex(x1, y1, cr, cg, cb, t->alpha);
                            PushVertex(x0, y1, cr, cg, cb, t->alpha);
                        } else {
                            col++;
                        }
                    }
                }

                SelectObject(g_gdi_hdc, old_dib);
                DeleteObject(dib);
            }

            cursor_x += (float)char_sz.cx;
        }

        SelectObject(g_gdi_hdc, old_font);
        DeleteObject(font);
    }
}
