/* Minimal scriptable input plugin for mupen64plus: buttons are set by the frontend via SetButtons(). */
#include <stdint.h>
#include <string.h>

#define EXPORT __attribute__((visibility("default")))
#define CALL

typedef struct { int Present; int RawData; int Plugin; int Type; } CONTROL;
typedef struct { CONTROL *Controls; } CONTROL_INFO;
typedef union { unsigned int Value; } BUTTONS;

static volatile uint32_t g_buttons[4];

EXPORT void SetButtons(int ctrl, uint32_t v) { if (ctrl >= 0 && ctrl < 4) g_buttons[ctrl] = v; }

EXPORT int CALL PluginStartup(void *h, void *ctx, void *cb) { return 0; }
EXPORT int CALL PluginShutdown(void) { return 0; }
EXPORT int CALL PluginGetVersion(int *type, int *ver, int *api, const char **name, int *caps)
{
    if (type) *type = 4; /* M64PLUGIN_INPUT */
    if (ver) *ver = 0x020000;
    if (api) *api = 0x020101;
    if (name) *name = "Script Input";
    if (caps) *caps = 0;
    return 0;
}
EXPORT void CALL InitiateControllers(CONTROL_INFO info)
{
    for (int i = 0; i < 4; i++) {
        info.Controls[i].Present = (i == 0);
        info.Controls[i].RawData = 0;
        info.Controls[i].Plugin = 1; /* PLUGIN_NONE */
        info.Controls[i].Type = 0;
    }
}
EXPORT void CALL GetKeys(int Control, BUTTONS *Keys) { Keys->Value = g_buttons[Control & 3]; }
EXPORT void CALL ControllerCommand(int Control, unsigned char *Command) {}
EXPORT void CALL ReadController(int Control, unsigned char *Command) {}
EXPORT int CALL RomOpen(void) { return 1; }
EXPORT void CALL RomClosed(void) {}
EXPORT void CALL SDL_KeyDown(int keymod, int keysym) {}
EXPORT void CALL SDL_KeyUp(int keymod, int keysym) {}
EXPORT void CALL RenderCallback(void) {}
