#include "platform.h"
#include <math.h>
#include <stdlib.h>

static int screenW = 800, screenH = 600;
static HWND hwnd;
static HDC hdc;
static HDC memDC;
static HBITMAP memBmp;

typedef struct { float x, y, hw, hh, rot; int r, g, b; } Rect;
typedef struct { float x, y, radius; int r, g, b; } Circle;
typedef struct { float x1, y1, x2, y2; int width, r, g, b; } LineObj;
typedef struct { float x1, y1, x2, y2; int width, r, g, b; } Arrow;
typedef struct { char text[256]; float x, y; int size, r, g, b; } TextObj;

static Rect* shapes = NULL;
static Circle* circles = NULL;
static LineObj* lines = NULL;
static Arrow* arrows = NULL;
static TextObj* texts = NULL;

static int shapeCount = 0, circleCount = 0, lineCount = 0, arrowCount = 0, textCount = 0;
static int shapeCap = 0, circleCap = 0, lineCap = 0, arrowCap = 0, textCap = 0;

static void resizeRects(){ if(shapeCount < shapeCap) return; shapeCap = shapeCap ? shapeCap*2 : 64; shapes = realloc(shapes, shapeCap*sizeof(Rect)); }
static void resizeCircles(){ if(circleCount < circleCap) return; circleCap = circleCap ? circleCap*2 : 64; circles = realloc(circles, circleCap*sizeof(Circle)); }
static void resizeLines(){ if(lineCount < lineCap) return; lineCap = lineCap ? lineCap*2 : 64; lines = realloc(lines, lineCap*sizeof(LineObj)); }
static void resizeArrows(){ if(arrowCount < arrowCap) return; arrowCap = arrowCap ? arrowCap*2 : 64; arrows = realloc(arrows, arrowCap*sizeof(Arrow)); }
static void resizeTexts(){ if(textCount < textCap) return; textCap = textCap ? textCap*2 : 16; texts = realloc(texts, textCap*sizeof(TextObj)); }

LRESULT CALLBACK WndProc(HWND h, UINT m, WPARAM w, LPARAM l) {
    if (m == WM_CLOSE) PostQuitMessage(0);
    return DefWindowProcA(h, m, w, l);
}

void Vulkan_Init(int w, int h) {
    screenW = w; screenH = h;
    HINSTANCE inst = GetModuleHandleA(NULL);

    WNDCLASSEXA wc = {0};
    wc.cbSize = sizeof(wc);
    wc.lpfnWndProc = WndProc;
    wc.hInstance = inst;
    wc.lpszClassName = "ManimVK";
    wc.hbrBackground = (HBRUSH)(COLOR_BACKGROUND);
    RegisterClassExA(&wc);

    hwnd = CreateWindowExA(0, "ManimVK", "Manim Live", WS_OVERLAPPEDWINDOW, 100,100,w,h,0,0,inst,0);
    hdc = GetDC(hwnd);
    memDC = CreateCompatibleDC(hdc);
    memBmp = CreateCompatibleBitmap(hdc, w, h);
    SelectObject(memDC, memBmp);
    ShowWindow(hwnd, 1);
}

void AddRect(float x, float y, float hw, float hh, float rot, int r,int g,int b) { resizeRects(); shapes[shapeCount++] = (Rect){x,y,hw,hh,rot,r,g,b}; }
void AddCircle(float x, float y, float radius, int r,int g,int b) { resizeCircles(); circles[circleCount++] = (Circle){x,y,radius,r,g,b}; }
void AddLine(float x1, float y1, float x2, float y2, int width, int r,int g,int b) { resizeLines(); lines[lineCount++] = (LineObj){x1,y1,x2,y2,width,r,g,b}; }
void AddArrow(float x1, float y1, float x2, float y2, int width, int r,int g,int b) { resizeArrows(); arrows[arrowCount++] = (Arrow){x1,y1,x2,y2,width,r,g,b}; }
void AddText(const char* text, float x, float y, int size, int r,int g,int b) {
    resizeTexts();
    strncpy(texts[textCount].text, text, sizeof(texts[textCount].text)-1);
    texts[textCount].x = x;
    texts[textCount].y = y;
    texts[textCount].size = size;
    texts[textCount].r = r;
    texts[textCount].g = g;
    texts[textCount].b = b;
    textCount++;
}

static void clearAll() {
    shapeCount = circleCount = lineCount = arrowCount = textCount = 0;
}

static void ndc_to_screen(float nx, float ny, LONG* sx, LONG* sy) {
    *sx = (LONG)(screenW/2.0f + nx * screenW/2.0f);
    *sy = (LONG)(screenH/2.0f + ny * screenH/2.0f);
}

int Vulkan_Tick() {
    MSG msg;
    while (PeekMessageA(&msg,NULL,0,0,PM_REMOVE)) { TranslateMessage(&msg); DispatchMessageA(&msg); }
    if (!IsWindow(hwnd)) return 0;

    RECT rc = {0,0,screenW,screenH};
    HBRUSH bg = CreateSolidBrush(RGB(12,18,35));
    FillRect(memDC, &rc, bg);
    DeleteObject(bg);

    // 直线
    for(int i=0; i<lineCount; i++){
        LineObj li = lines[i];
        LONG sx1,sy1,sx2,sy2;
        ndc_to_screen(li.x1, li.y1, &sx1, &sy1);
        ndc_to_screen(li.x2, li.y2, &sx2, &sy2);
        HPEN pen = CreatePen(PS_SOLID, li.width, RGB(li.r,li.g,li.b));
        HGDIOBJ old = SelectObject(memDC, pen);
        MoveToEx(memDC, sx1, sy1, NULL); LineTo(memDC, sx2, sy2);
        SelectObject(memDC, old); DeleteObject(pen);
    }

    // 箭头
    for(int i=0; i<arrowCount; i++){
        Arrow a = arrows[i];
        LONG sx1,sy1,sx2,sy2;
        ndc_to_screen(a.x1, a.y1, &sx1, &sy1);
        ndc_to_screen(a.x2, a.y2, &sx2, &sy2);
        HPEN pen = CreatePen(PS_SOLID, a.width, RGB(a.r,a.g,a.b));
        HGDIOBJ op = SelectObject(memDC, pen);
        HBRUSH ob = SelectObject(memDC, GetStockObject(DC_BRUSH));
        SetDCBrushColor(memDC, RGB(a.r,a.g,a.b));
        MoveToEx(memDC, sx1,sy1,NULL); LineTo(memDC, sx2,sy2);
        float dx = sx2-sx1, dy = sy2-sy1, len = sqrtf(dx*dx+dy*dy); if(len<1)len=1;
        float ux=dx/len, uy=dy/len;
        float ax=sx2-ux*12, ay=sy2-uy*12;
        float px=ax-uy*10, py=ay+ux*10, qx=ax+uy*10, qy=ay-ux*10;
        POINT pts[3]={{sx2,sy2},{(LONG)px,(LONG)py},{(LONG)qx,(LONG)qy}};
        Polygon(memDC, pts,3);
        SelectObject(memDC, op); SelectObject(memDC, ob); DeleteObject(pen);
    }

    // 圆形
    for (int i=0;i<circleCount;++i) {
        Circle c = circles[i]; LONG cx,cy; ndc_to_screen(c.x,c.y,&cx,&cy);
        int r = (int)(c.radius * screenW/2);
        HBRUSH br = CreateSolidBrush(RGB(c.r,c.g,c.b));
        HBRUSH old = SelectObject(memDC, br);
        Ellipse(memDC, cx-r,cy-r,cx+r,cy+r);
        SelectObject(memDC, old); DeleteObject(br);
    }

    // 矩形
    for (int i=0;i<shapeCount;++i) {
        Rect s = shapes[i];
        float c = cosf(s.rot), sr = sinf(s.rot);
        POINT pts[4];
        float ox=s.x, oy=s.y;
        pts[0].x = screenW/2 + (ox + (-s.hw*c + s.hh*sr)) * screenW/2;
        pts[0].y = screenH/2 + (oy + (-s.hw*sr - s.hh*c)) * screenH/2;
        pts[1].x = screenW/2 + (ox + ( s.hw*c + s.hh*sr)) * screenW/2;
        pts[1].y = screenH/2 + (oy + ( s.hw*sr - s.hh*c)) * screenH/2;
        pts[2].x = screenW/2 + (ox + ( s.hw*c - s.hh*sr)) * screenW/2;
        pts[2].y = screenH/2 + (oy + ( s.hw*sr + s.hh*c)) * screenH/2;
        pts[3].x = screenW/2 + (ox + (-s.hw*c - s.hh*sr)) * screenW/2;
        pts[3].y = screenH/2 + (oy + (-s.hw*sr + s.hh*c)) * screenH/2;
        HBRUSH br = CreateSolidBrush(RGB(s.r,s.g,s.b));
        HPEN pen = CreatePen(PS_SOLID,2,RGB(255,255,255));
        HGDIOBJ ob=SelectObject(memDC,br), op=SelectObject(memDC,pen);
        Polygon(memDC,pts,4);
        SelectObject(memDC,ob); SelectObject(memDC,op);
        DeleteObject(pen); DeleteObject(br);
    }

    // ✅ 文字
    for(int i=0; i<textCount; i++){
        TextObj t = texts[i];
        LONG sx, sy;
        ndc_to_screen(t.x, t.y, &sx, &sy);

        HFONT font = CreateFontA(t.size, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
            ANSI_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            DEFAULT_QUALITY, DEFAULT_PITCH | FF_SWISS, "Consolas");
        HGDIOBJ oldFont = SelectObject(memDC, font);

        SetTextColor(memDC, RGB(t.r, t.g, t.b));
        SetBkMode(memDC, TRANSPARENT);

        TextOutA(memDC, sx, sy, t.text, strlen(t.text));

        SelectObject(memDC, oldFont);
        DeleteObject(font);
    }

    BitBlt(hdc,0,0,screenW,screenH, memDC,0,0,SRCCOPY);
    clearAll();
    return 1;
}

void Vulkan_Shutdown() {
    free(shapes); free(circles); free(lines); free(arrows); free(texts);
    DeleteDC(memDC);
    DeleteObject(memBmp);
    ReleaseDC(hwnd,hdc);
    DestroyWindow(hwnd);
}