import win32api
import win32con


def click_mouse_with_coordinates(x, y):
    win32api.SetCursorPos((int(x), int(y)))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def right_click_mouse_with_coordinates(x, y):
    win32api.SetCursorPos((int(x), int(y)))
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

def space_bar():
    win32api.keybd_event(0x20, 0, 0, 0)
    win32api.keybd_event(0x20, 0, win32con.KEYEVENTF_KEYUP, 0)
