#include "platform.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

static int screenW = 800, screenH = 600;
static HWND hwnd;
static HDC hdc;
static HDC memDC;
static HBITMAP memBmp;

typedef struct { float x, y, hw, hh, rot; int r, g, b; } Rect;
typedef struct { float x, y, radius; int r, g, b; } Circle;
typedef struct { float x1, y1, x2, y2; int width, r, g, b; } LineObj;
typedef struct { float x1, y1, x2, y2; int width, r, g, b; } ArrowObj;
typedef struct { char text[256]; float x, y; int size, r, g, b; } TextObj;

typedef struct {
    float x, y, hw, hh, rot;
    int fr, fg, fb;
    int sr, sg, sb;
    int strokeWidth;
} SepRect;

typedef struct {
    float x, y, radius;
    int fr, fg, fb;
    int sr, sg, sb;
    int strokeWidth;
} SepCircle;

typedef struct {
    float* points;
    int count;
    int fr, fg, fb;
    int sr, sg, sb;
    int strokeWidth;
} SepPolygon;

static Rect* shapes = NULL;
static Circle* circles = NULL;
static LineObj* lines = NULL;
static ArrowObj* arrows = NULL;
static TextObj* texts = NULL;
static SepRect* sepRects = NULL;
static SepCircle* sepCircles = NULL;
static SepPolygon* sepPolygons = NULL;

static int shapeCount = 0, circleCount = 0, lineCount = 0, arrowCount = 0, textCount = 0;
static int sepRectCount = 0, sepCircleCount = 0, sepPolygonCount = 0;

static int shapeCap = 0, circleCap = 0, lineCap = 0, arrowCap = 0, textCap = 0;
static int sepRectCap = 0, sepCircleCap = 0, sepPolygonCap = 0;

static void resizeShapes()  { if (shapeCount >= shapeCap)  { shapeCap = shapeCap ? shapeCap*2 : 64;  shapes = realloc(shapes, shapeCap * sizeof(Rect)); } }
static void resizeCircles() { if (circleCount >= circleCap) { circleCap = circleCap ? circleCap*2 : 64; circles = realloc(circles, circleCap * sizeof(Circle)); } }
static void resizeLines()   { if (lineCount >= lineCap)   { lineCap = lineCap ? lineCap*2 : 64;   lines = realloc(lines, lineCap * sizeof(LineObj)); } }
static void resizeArrows()  { if (arrowCount >= arrowCap) { arrowCap = arrowCap ? arrowCap*2 : 64; arrows = realloc(arrows, arrowCap * sizeof(ArrowObj)); } }
static void resizeTexts()   { if (textCount >= textCap)   { textCap = textCap ? textCap*2 : 16;   texts = realloc(texts, textCap * sizeof(TextObj)); } }
static void resizeSepRects(){ if (sepRectCount >= sepRectCap) { sepRectCap = sepRectCap ? sepRectCap*2 : 32; sepRects = realloc(sepRects, sepRectCap * sizeof(SepRect)); } }
static void resizeSepCircles(){ if (sepCircleCount >= sepCircleCap) { sepCircleCap = sepCircleCap ? sepCircleCap*2 : 32; sepCircles = realloc(sepCircles, sepCircleCap * sizeof(SepCircle)); } }
static void resizeSepPolygons(){ if (sepPolygonCount >= sepPolygonCap) { sepPolygonCap = sepPolygonCap ? sepPolygonCap*2 : 32; sepPolygons = realloc(sepPolygons, sepPolygonCap * sizeof(SepPolygon)); } }

static void manim_to_win(float x, float y, int *sx, int *sy) {
    float scale = 200.0f;
    *sx = (int)(screenW / 2 + x * scale);
    *sy = (int)(screenH / 2 - y * scale);
}

LRESULT CALLBACK WndProc(HWND h, UINT m, WPARAM w, LPARAM l) {
    if (m == WM_CLOSE) PostQuitMessage(0);
    return DefWindowProcA(h, m, w, l);
}

void Vulkan_Init(int w, int h) {
    screenW = w;
    screenH = h;
    HINSTANCE inst = GetModuleHandleA(NULL);

    WNDCLASSEXA wc = {0};
    wc.cbSize = sizeof(wc);
    wc.lpfnWndProc = WndProc;
    wc.hInstance = inst;
    wc.lpszClassName = "ManimVK";
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    RegisterClassExA(&wc);

    hwnd = CreateWindowExA(0, wc.lpszClassName, "Manim Live", WS_OVERLAPPEDWINDOW, 100, 100, w, h, 0, 0, inst, 0);
    hdc = GetDC(hwnd);
    memDC = CreateCompatibleDC(hdc);
    memBmp = CreateCompatibleBitmap(hdc, w, h);
    SelectObject(memDC, memBmp);
    ShowWindow(hwnd, SW_SHOW);
}

void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b) { resizeShapes(); shapes[shapeCount++] = (Rect){x,y,hw,hh,rot,r,g,b}; }
void AddCircle(float x, float y, float radius, int r, int g, int b) { resizeCircles(); circles[circleCount++] = (Circle){x,y,radius,r,g,b}; }
void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b) { resizeLines(); lines[lineCount++] = (LineObj){x1,y1,x2,y2,width,r,g,b}; }
void AddArrow(float x1, float y1, float x2, float y2, int width, int r, int g, int b) { resizeArrows(); arrows[arrowCount++] = (ArrowObj){x1,y1,x2,y2,width,r,g,b}; }

void AddText(const char* text, float x, float y, int size, int r, int g, int b) {
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

void AddRectSeparate(float x, float y, float hw, float hh, float rot, int fr, int fg, int fb, int sr, int sg, int sb, int sw) {
    resizeSepRects();
    sepRects[sepRectCount++] = (SepRect){x,y,hw,hh,rot,fr,fg,fb,sr,sg,sb,sw};
}

void AddCircleSeparate(float x, float y, float radius, int fr, int fg, int fb, int sr, int sg, int sb, int sw) {
    resizeSepCircles();
    sepCircles[sepCircleCount++] = (SepCircle){x,y,radius,fr,fg,fb,sr,sg,sb,sw};
}

void AddPolygonSeparate(float* points, int count, int fr, int fg, int fb, int sr, int sg, int sb, int strokeWidth) {
    resizeSepPolygons();
    SepPolygon* p = &sepPolygons[sepPolygonCount++];
    p->count = count;
    p->fr = fr; p->fg = fg; p->fb = fb;
    p->sr = sr; p->sg = sg; p->sb = sb;
    p->strokeWidth = strokeWidth;
    p->points = malloc(sizeof(float)*2*count);
    for(int i=0;i<2*count;i++) p->points[i] = points[i];
}

static void clearAll() {
    shapeCount = circleCount = lineCount = arrowCount = textCount = 0;
    sepRectCount = sepCircleCount = sepPolygonCount = 0;
}

int Vulkan_Tick() {
    MSG msg;
    while (PeekMessageA(&msg, NULL, 0, 0, PM_REMOVE)) { TranslateMessage(&msg); DispatchMessage(&msg); }
    if (msg.message == WM_QUIT) return 0;

    RECT rc = {0,0,screenW,screenH};
    FillRect(memDC, &rc, (HBRUSH)GetStockObject(BLACK_BRUSH));

    for (int i=0;i<lineCount;i++) {
        LineObj li = lines[i];
        int x1,y1,x2,y2;
        manim_to_win(li.x1, li.y1, &x1, &y1);
        manim_to_win(li.x2, li.y2, &x2, &y2);
        HPEN pen = CreatePen(PS_SOLID, li.width, RGB(li.r,li.g,li.b));
        HGDIOBJ old = SelectObject(memDC, pen);
        MoveToEx(memDC, x1, y1, NULL);
        LineTo(memDC, x2, y2);
        SelectObject(memDC, old);
        DeleteObject(pen);
    }

    for (int i=0;i<arrowCount;i++) {
        ArrowObj a = arrows[i];
        int x1,y1,x2,y2;
        manim_to_win(a.x1,a.y1,&x1,&y1);
        manim_to_win(a.x2,a.y2,&x2,&y2);
        HPEN pen = CreatePen(PS_SOLID, a.width, RGB(a.r,a.g,a.b));
        HGDIOBJ op = SelectObject(memDC, pen);
        MoveToEx(memDC,x1,y1,NULL); LineTo(memDC,x2,y2);
        float dx = x2-x1, dy = y2-y1;
        float len = sqrtf(dx*dx+dy*dy); if(len<1)len=1;
        float ux = dx/len, uy=dy/len;
        float px = x2-ux*15, py = y2-uy*15;
        POINT pts[3] = {{x2,y2},{(LONG)(px-uy*10),(LONG)(py+ux*10)},{(LONG)(px+uy*10),(LONG)(py-ux*10)}};
        HBRUSH br = CreateSolidBrush(RGB(a.r,a.g,a.b));
        HGDIOBJ ob = SelectObject(memDC, br);
        Polygon(memDC, pts,3);
        SelectObject(memDC,op); SelectObject(memDC,ob);
        DeleteObject(pen); DeleteObject(br);
    }

    for (int i=0;i<circleCount;i++) {
        Circle c = circles[i];
        int cx,cy; manim_to_win(c.x,c.y,&cx,&cy);
        int r = (int)(c.radius*200);
        HBRUSH br = CreateSolidBrush(RGB(c.r,c.g,c.b));
        HGDIOBJ old = SelectObject(memDC, br);
        Ellipse(memDC, cx-r, cy-r, cx+r, cy+r);
        SelectObject(memDC, old);
        DeleteObject(br);
    }

    for (int i=0;i<shapeCount;i++) {
        Rect s = shapes[i];
        int cx,cy; manim_to_win(s.x,s.y,&cx,&cy);
        float hw = s.hw*200, hh = s.hh*200;
        float c = cosf(s.rot), sn=sinf(s.rot);
        POINT pts[4] = {
            {cx+(int)(-hw*c-hh*sn), cy+(int)(-hw*sn+hh*c)},
            {cx+(int)(hw*c-hh*sn), cy+(int)(hw*sn+hh*c)},
            {cx+(int)(hw*c+hh*sn), cy+(int)(hw*sn-hh*c)},
            {cx+(int)(-hw*c+hh*sn), cy+(int)(-hw*sn-hh*c)}
        };
        HBRUSH br = CreateSolidBrush(RGB(s.r,s.g,s.b));
        HPEN pen = CreatePen(PS_SOLID,2,RGB(255,255,255));
        HGDIOBJ ob=SelectObject(memDC,br), op=SelectObject(memDC,pen);
        Polygon(memDC,pts,4);
        SelectObject(memDC,ob); SelectObject(memDC,op);
        DeleteObject(pen); DeleteObject(br);
    }

    for (int i=0;i<sepRectCount;i++) {
        SepRect s = sepRects[i];
        int cx,cy; manim_to_win(s.x,s.y,&cx,&cy);
        float hw = s.hw*200, hh = s.hh*200;
        float c = cosf(s.rot), sn=sinf(s.rot);
        POINT pts[4] = {
            {cx+(int)(-hw*c-hh*sn), cy+(int)(-hw*sn+hh*c)},
            {cx+(int)(hw*c-hh*sn), cy+(int)(hw*sn+hh*c)},
            {cx+(int)(hw*c+hh*sn), cy+(int)(hw*sn-hh*c)},
            {cx+(int)(-hw*c+hh*sn), cy+(int)(-hw*sn-hh*c)}
        };
        HPEN pen = CreatePen(PS_SOLID, s.strokeWidth, RGB(s.sr,s.sg,s.sb));
        HBRUSH br = CreateSolidBrush(RGB(s.fr,s.fg,s.fb));
        HGDIOBJ op=SelectObject(memDC,pen), ob=SelectObject(memDC,br);
        Polygon(memDC,pts,4);
        SelectObject(memDC,op); SelectObject(memDC,ob);
        DeleteObject(pen); DeleteObject(br);
    }

    for (int i=0;i<sepCircleCount;i++) {
        SepCircle c = sepCircles[i];
        int cx,cy; manim_to_win(c.x,c.y,&cx,&cy);
        int rad = (int)(c.radius*200);
        HPEN pen = CreatePen(PS_SOLID, c.strokeWidth, RGB(c.sr,c.sg,c.sb));
        HBRUSH br = CreateSolidBrush(RGB(c.fr,c.fg,c.fb));
        HGDIOBJ op=SelectObject(memDC,pen), ob=SelectObject(memDC,br);
        Ellipse(memDC, cx-rad, cy-rad, cx+rad, cy+rad);
        SelectObject(memDC,op); SelectObject(memDC,ob);
        DeleteObject(pen); DeleteObject(br);
    }

    for (int i=0;i<sepPolygonCount;i++) {
        SepPolygon p = sepPolygons[i];
        POINT* pts = malloc(sizeof(POINT)*p.count);
        for(int j=0;j<p.count;j++){
            int sx,sy;
            manim_to_win(p.points[2*j], p.points[2*j+1], &sx, &sy);
            pts[j].x = sx;
            pts[j].y = sy;
        }
        HPEN pen = CreatePen(PS_SOLID, p.strokeWidth, RGB(p.sr,p.sg,p.sb));
        HBRUSH br = CreateSolidBrush(RGB(p.fr,p.fg,p.fb));
        HGDIOBJ op=SelectObject(memDC,pen), ob=SelectObject(memDC,br);
        Polygon(memDC, pts, p.count);
        SelectObject(memDC,op); SelectObject(memDC,ob);
        DeleteObject(pen); DeleteObject(br);
        free(pts);
    }

    for(int i=0;i<textCount;i++){
        TextObj t=texts[i];
        int x,y; manim_to_win(t.x,t.y,&x,&y);
        HFONT f=CreateFontA(t.size,0,0,0,FW_BOLD,0,0,0,ANSI_CHARSET,OUT_DEFAULT_PRECIS,CLIP_DEFAULT_PRECIS,DEFAULT_QUALITY,DEFAULT_PITCH|FF_SWISS,"Consolas");
        HGDIOBJ old=SelectObject(memDC,f);
        SetTextColor(memDC,RGB(t.r,t.g,t.b));
        SetBkMode(memDC,TRANSPARENT);
        TextOutA(memDC,x,y,t.text,strlen(t.text));
        SelectObject(memDC,old);
        DeleteObject(f);
    }

    BitBlt(hdc,0,0,screenW,screenH,memDC,0,0,SRCCOPY);
    clearAll();
    return 1;
}

void Vulkan_Shutdown() {
    free(shapes); free(circles); free(lines); free(arrows); free(texts);
    free(sepRects); free(sepCircles);
    for(int i=0;i<sepPolygonCount;i++) free(sepPolygons[i].points);
    free(sepPolygons);
    DeleteDC(memDC);
    DeleteObject(memBmp);
    ReleaseDC(hwnd,hdc);
    DestroyWindow(hwnd);
}