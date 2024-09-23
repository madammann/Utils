import win32gui
import win32ui
import win32con
import win32api
import win32process
import time
import difflib
import subprocess
import os

from PIL import Image

import numpy as np

try:
    import easyocr
except:
    print('WARNING: Optic Character Recognition capabilities are not enabled, make sure easyocr library is installed.')

def initialize_ocr_reader(language=['en'], gpu=True):
    return easyocr.Reader(language,gpu=gpu)

class Handler:
    '''
    Important note: Multithreading is forbidden in this module!
    '''
    
    def __init__(self, path=''):
        self.path = os.path.normpath(path)
        if path != '':
            self.hwnd = self.create_window(self.path)
        
        self.NON_RESPONDING_TIMEOUT = 120
        self.FOREGROUND_MODE = False
        self.MULTIPROCESSING_ID = 1
        self.DOUBLE_CLICK_TIME = win32gui.GetDoubleClickTime()

    '''WINDOW METHODS - BOOLEAN'''
    def is_open(self):
        if win32gui.IsWindow(self.hwnd):
            return True
        return False

    def is_responsive(self):
        if win32gui.IsWindowEnabled(self.hwnd):
            return True
        start = time.time_ns()
        while not win32gui.IsWindowEnabled(self.hwnd):
            time.sleep(1)
            if (time.time_ns()-start) > self.NON_RESPONDING_TIMEOUT*1e9:
                return False

        if win32gui.IsWindowEnabled(self.hwnd):
            return True
        return False

    def is_visible(self):
        if win32gui.IsWindowVisible(self.hwnd):
            return True
        return False

    def is_minimized(self):
        placement = win32gui.GetWindowPlacement(self.hwnd)
        return placement[1] == win32con.SW_SHOWMINIMIZED

    '''WINDOW METHODS - SETTER'''
    def minimize(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)

    def maximize(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)

    def move(self, x, y, width, height, redraw=True):
        '''
        Moves the position of the window.
        '''
        if isinstance(x, float) and x > 0:
            pass

        if isinstance(y, float) and y > 0:
            pass
            
        win32gui.MoveWindow(self.hwnd, x, y, width, height, redraw)

    def change_resolution(self, x, y, redraw=True):
        win32gui.MoveWindow(self.hwnd, x, y, width, height, redraw)
        
    '''SCREENSHOT METHODS'''
    def background_screenshot(self):
        wdc = win32gui.GetWindowDC(self.hwnd)
        dc_obj=win32ui.CreateDCFromHandle(wdc)
        cdc=dc_obj.CreateCompatibleDC()
        
        bmp = win32ui.CreateBitmap()
        width, height = self.resolution
        bmp.CreateCompatibleBitmap(dc_obj, width, height)
        cdc.SelectObject(bmp)
        cdc.BitBlt((0,0),(width, height) , dc_obj, (0,0), win32con.SRCCOPY)
        
        bmp_info = bmp.GetInfo()
        bmp_str = bmp.GetBitmapBits(True)
        img = Image.frombuffer('RGBA', (bmp_info['bmWidth'], bmp_info['bmHeight']), bmp_str, 'raw', 'RGBA', 0, 1)
    
    
        # dataBitMap.SaveBitmapFile(cDC, 'screenshot.bmp')
        dc_obj.DeleteDC()
        cdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wdc)
        win32gui.DeleteObject(bmp.GetHandle())
    
        return img

    def foreground_screenshot(self):
        raise NotImplementedError('This functionality is not yet added.')
    
    '''PROPERTIES GETTER'''
    
    @property
    def window_name(self):
        return win32gui.GetWindowText(self.hwnd)
        
    @property
    def resolution(self):
        _, _, width, height = win32gui.GetWindowRect(self.hwnd)
        return width, height

    @property
    def position(self):
        x, y, _, _ = win32gui.GetWindowRect(self.hwnd)
        return x, y

    @property
    def x(self):
        x, _, _, _ = win32gui.GetWindowRect(self.hwnd)
        return x

    @property
    def y(self):
        _, y, _, _ = win32gui.GetWindowRect(self.hwnd)
        return y

    @property
    def width(self):
        _, _, width, _ = win32gui.GetWindowRect(self.hwnd)
        return width

    @property
    def height(self):
        _, _, _, height = win32gui.GetWindowRect(self.hwnd)
        return height

    
    '''WINDOW SPAWN OR FINDER'''
    
    def create_window(self, path):
        '''
        ADD
        '''

        process = subprocess.Popen(path)
        time.sleep(1)
        self.hwnd = self.get_window_by_pid(process.pid)
        
        return self.hwnd
    
    def get_window_by_pid(self, pid) -> int:
        '''
        ADD
        '''
        results = {}
        win32gui.EnumWindows(
            lambda hwnd, _: results.update({win32process.GetWindowThreadProcessId(hwnd)[1] : hwnd}) if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd) else None,
            0
        )
        
        if pid in results.keys():
            self.hwnd = results[pid]
            self.tid, self.pid = win32process.GetWindowThreadProcessId(self.hwnd)
            return self.hwnd

        raise ValueError(f'Not possible to find window handle by process id {pid}, window may no longer exist or wrong process id was provided.')

    def get_window_by_title(self, st : str) -> int:
        '''
        Finds the window of an open application based on a window title input string.

        Param:
            st (str): Search term for the window title, the closest window will be chosen based on difflib.SequenceMatcher.
        Returns:
            hwnd (int): The window handle with the highest matching probability to the search term.
        '''
        results = []
        win32gui.EnumWindows(
            lambda hwnd, _: results.append((hwnd, win32gui.GetWindowText(hwnd))) if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd) else None,
            0
        )

        confs = []
        for hwnd, title in results:
            confs += [difflib.SequenceMatcher(lambda s: s == '', st, title).ratio()]
    
        if len(results) <= 0:
            raise ValueError(f'Unable to find window handle "{self.name}", application may be closed or minimized during search for it.')
        else:
            self.hwnd = results[int(np.argmax(confs))][0]
            self.tid, self.pid = win32process.GetWindowThreadProcessId(self.hwnd)
            return self.hwnd
            
        raise ValueError(f'Something went wrong in retrieving the window handle, this error is most likely a OS related error.')

    def close_window(self):
        '''
        Tries to close a window first with a message protocol send to the window and then, after a 5s timeout, tries to terminate the process directly.
        '''
        try:
            result = win32gui.SendMessageTimeout(self.hwnd, win32con.WM_CLOSE, 0, 0, win32con.SMTO_ABORTIFHUNG, 5000)
        except pywintypes.error:
            try:
                _, pid = win32process.GetWindowThreadProcessId(self.hwnd)
                hProcess = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, pid)
                win32api.TerminateProcess(hProcess, 0)
                win32api.CloseHandle(hProcess)
                win32gui.CloseWindow(self.hwnd)
            except Exception as e:
                raise e