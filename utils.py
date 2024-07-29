import win32gui
import win32con

def make_window_transparent(root):
    hwnd = win32gui.FindWindow(None, root.title())
    if hwnd:
        # Set layered window attributes
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                               win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(hwnd, 0x00FFFFFF, 0, win32con.LWA_COLORKEY)
    else:
        print("Window handle not found")

def make_window_clickable(root):
    hwnd = win32gui.FindWindow(None, root.title())
    if hwnd:
        extended_style_settings = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        extended_style_settings &= ~win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style_settings)
    else:
        print("Window handle not found")
