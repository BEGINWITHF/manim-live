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
typedef struct { char text[256]; float x, y; int size, r, g, b; } TextObj;

static Rect* shapes = NULL;
static Circle* circles = NULL;
static LineObj* lines = NULL;
static TextObj* texts = NULL;

static int shapeCount=0, circleCount=0, lineCount=0, textCount=0;
static int shapeCap=0, circleCap=0, lineCap=0, textCap=0;

static void resizeRects(){if(shapeCount>=shapeCap){shapeCap=shapeCap?shapeCap*2:64;shapes=realloc(shapes,shapeCap*sizeof(Rect));}}
static void resizeCircles(){if(circleCount>=circleCap){circleCap=circleCap?circleCap*2:64;circles=realloc(circles,circleCap*sizeof(Circle));}}
static void resizeLines(){if(lineCount>=lineCap){lineCap=lineCap?lineCap*2:64;lines=realloc(lines,lineCap*sizeof(LineObj));}}
static void resizeTexts(){if(textCount>=textCap){textCap=textCap?textCap*2:16;texts=realloc(texts,textCap*sizeof(TextObj));}}

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
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW+1);
    RegisterClassExA(&wc);

    hwnd = CreateWindowExA(0, wc.lpszClassName, "Manim Live", WS_OVERLAPPEDWINDOW, 100,100,w,h,0,0,inst,0);
    hdc = GetDC(hwnd);
    memDC = CreateCompatibleDC(hdc);
    memBmp = CreateCompatibleBitmap(hdc, w, h);
    SelectObject(memDC, memBmp);
    ShowWindow(hwnd, SW_SHOW);
}

static void manim_to_win(float x, float y, int *sx, int *sy) {
    float scale = 200.0f;
    *sx = (int)(screenW/2 + x*scale);
    *sy = (int)(screenH/2 - y*scale);
}

void AddRect(float x, float y, float hw, float hh, float rot, int r,int g,int b) { resizeRects(); shapes[shapeCount++] = (Rect){x,y,hw,hh,rot,r,g,b}; }
void AddCircle(float x, float y, float radius, int r,int g,int b) { resizeCircles(); circles[circleCount++] = (Circle){x,y,radius,r,g,b}; }
void AddLine(float x1, float y1, float x2, float y2, int width, int r,int g,int b) { resizeLines(); lines[lineCount++] = (LineObj){x1,y1,x2,y2,width,r,g,b}; }
void AddText(const char* text, float x, float y, int size, int r,int g,int b) {
    resizeTexts();
    strncpy(texts[textCount].text, text, sizeof(texts[textCount].text)-1);
    texts[textCount].x = x; texts[textCount].y = y;
    texts[textCount].size = size;
    texts[textCount].r = r; texts[textCount].g = g; texts[textCount].b = b;
    textCount++;
}

static void clearAll() { shapeCount=circleCount=lineCount=textCount=0; }

int Vulkan_Tick() {
    MSG msg;
    while (PeekMessageA(&msg,NULL,0,0,PM_REMOVE)) { TranslateMessage(&msg); DispatchMessageA(&msg); }
    if (msg.message == WM_QUIT) return 0;

    RECT rc = {0,0,screenW,screenH};
    FillRect(memDC, &rc, (HBRUSH)GetStockObject(BLACK_BRUSH));

    for(int i=0;i<lineCount;i++){
        LineObj li = lines[i];
        int x1,y1,x2,y2;
        manim_to_win(li.x1,li.y1,&x1,&y1);
        manim_to_win(li.x2,li.y2,&x2,&y2);
        HPEN pen = CreatePen(PS_SOLID, li.width, RGB(li.r,li.g,li.b));
        HGDIOBJ old = SelectObject(memDC, pen);
        MoveToEx(memDC,x1,y1,NULL); LineTo(memDC,x2,y2);
        SelectObject(memDC,old); DeleteObject(pen);
    }

    for(int i=0;i<circleCount;i++){
        Circle c = circles[i];
        int cx,cy; manim_to_win(c.x,c.y,&cx,&cy);
        int r = (int)(c.radius*200);
        HBRUSH br = CreateSolidBrush(RGB(c.r,c.g,c.b));
        HGDIOBJ old = SelectObject(memDC,br);
        Ellipse(memDC,cx-r,cy-r,cx+r,cy+r);
        SelectObject(memDC,old); DeleteObject(br);
    }

    for(int i=0;i<shapeCount;i++){
        Rect s = shapes[i];
        int cx,cy; manim_to_win(s.x,s.y,&cx,&cy);
        float hw = s.hw*200, hh = s.hh*200, rot = s.rot;
        float c = cosf(rot), sn = sinf(rot);
        POINT pts[4] = {
            {cx+(int)(-hw*c-hh*sn), cy+(int)(-hw*sn+hh*c)},
            {cx+(int)( hw*c-hh*sn), cy+(int)( hw*sn+hh*c)},
            {cx+(int)( hw*c+hh*sn), cy+(int)( hw*sn-hh*c)},
            {cx+(int)(-hw*c+hh*sn), cy+(int)(-hw*sn-hh*c)}
        };
        HBRUSH br = CreateSolidBrush(RGB(s.r,s.g,s.b));
        HPEN pen = CreatePen(PS_SOLID,2,RGB(255,255,255));
        HGDIOBJ ob=SelectObject(memDC,br), op=SelectObject(memDC,pen);
        Polygon(memDC,pts,4);
        SelectObject(memDC,ob); SelectObject(memDC,op);
        DeleteObject(pen); DeleteObject(br);
    }

    for(int i=0;i<textCount;i++){
        TextObj t = texts[i];
        int x,y; manim_to_win(t.x,t.y,&x,&y);
        HFONT font = CreateFontA(t.size,0,0,0,FW_BOLD,0,0,0,ANSI_CHARSET,OUT_DEFAULT_PRECIS,CLIP_DEFAULT_PRECIS,DEFAULT_QUALITY,DEFAULT_PITCH|FF_SWISS,"Consolas");
        HGDIOBJ old = SelectObject(memDC,font);
        SetTextColor(memDC,RGB(t.r,t.g,t.b));
        SetBkMode(memDC,TRANSPARENT);
        TextOutA(memDC,x,y,t.text,strlen(t.text));
        SelectObject(memDC,old);
        DeleteObject(font);
    }

    BitBlt(hdc,0,0,screenW,screenH,memDC,0,0,SRCCOPY);
    clearAll();
    return 1;
}

void Vulkan_Shutdown() {
    free(shapes); free(circles); free(lines); free(texts);
    DeleteDC(memDC);
    DeleteObject(memBmp);
    ReleaseDC(hwnd,hdc);
    DestroyWindow(hwnd);
}