/* Headless VDAC: keeps the last output frame in memory for the test harness */
#include "output/vdac.h"
#include "output/screen.h"
#include <stdlib.h>
#include <string.h>
#define EXPORT __attribute__((visibility("default")))
static uint8_t* g_px; static uint32_t g_w, g_h, g_frames;
void vdac_init(struct n64video_config* config) {}
void vdac_read(struct n64video_frame_buffer* fb, bool alpha) { fb->width = g_w; fb->height = g_h; fb->valid = g_px != NULL; if (fb->pixels && g_px) memcpy(fb->pixels, g_px, g_w * g_h * 4); }
void vdac_write(struct n64video_frame_buffer* fb)
{
    if (!fb->valid) return;
    uint32_t w = fb->width, h = fb->height;
    if (w != g_w || h != g_h) { free(g_px); g_px = malloc(w * h * 4); g_w = w; g_h = h; }
    for (uint32_t y = 0; y < h; y++)
        memcpy(g_px + y * w * 4, (uint8_t*)fb->pixels + y * fb->pitch * 4, w * 4);
    g_frames++;
}
void vdac_sync(bool valid) {}
void vdac_close(void) {}
void screen_init(struct n64video_config* config) {}
void screen_adjust(int32_t a, int32_t b, int32_t* w, int32_t* h, int32_t* x, int32_t* y) {}
void screen_update(void) {}
void screen_toggle_fullscreen(void) {}
void screen_close(void) {}
EXPORT uint8_t* ALGetFrame(uint32_t* w, uint32_t* h, uint32_t* n) { *w = g_w; *h = g_h; *n = g_frames; return g_px; }
int32_t win_width = 640, win_height = 480, win_fullscreen = 0;
