from collections import namedtuple
from ctypes import wintypes

import psutil
import ctypes

ProcessInfo = namedtuple("ProcessInfo", ["id", "name"])

"""
   MMM List Comprehensions MMMM...
"""


class WinFunc:
    PROCESS_ALL_ACCESS = 0x1FFFFF

    def __init__(self) -> None:
        self._process_info: ProcessInfo = ProcessInfo(0, "")
        self._handle: int = 0
        self._hwnd: int = 0
        self._thread_id: int = 0
        self.dll_handle: int = 0
        self.hook: int = 0

    def set_process_by_name(self, name: str) -> None:
        self._process_info = ProcessInfo(self._find_process_id(name), name)

    def _find_process_id(self, name: str) -> int:
        return next(
            (proc.pid for proc in psutil.process_iter() if proc.name() == name), None
        ) or exec(f"raise ValueError(f\"Process '{name}' not found\")")

    def acquire_window_info(self) -> None:
        self._hwnd = ctypes.windll.user32.FindWindowA(None, b"Roblox")
        if not self._hwnd:
            raise ValueError("Roblox window not found")
        self._thread_id = ctypes.windll.user32.GetWindowThreadProcessId(
            self._hwnd, None
        )

    def acquire_handle(self) -> int:
        if not self._process_info.id:
            raise RuntimeError("Process ID not set")

        self._handle = ctypes.windll.kernel32.OpenProcess(
            self.PROCESS_ALL_ACCESS, False, self._process_info.id
        )
        return (
            self._handle
            if self._handle
            else exec(
                'raise OSError(f"Failed to open process {self._process_info.id}")'
            )
        )

    def load_dll(self, dll_path: str) -> int:
        kernel32 = ctypes.windll.kernel32
        kernel32.LoadLibraryExA.restype = ctypes.c_void_p
        self.dll_handle = kernel32.LoadLibraryExA(dll_path.encode(), None, 0)
        return (
            self.dll_handle
            if self.dll_handle
            else (
                self.release_handle(),
                exec(f'raise OSError("Failed to load DLL: {dll_path}")'),
            )[1]
        )

    def get_callback_address(self, callback_name: str) -> int:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetProcAddress.argtypes = (wintypes.HMODULE, wintypes.LPCSTR)
        kernel32.GetProcAddress.restype = ctypes.c_void_p

        func = (
            kernel32.GetProcAddress(
                ctypes.c_void_p(self.dll_handle), callback_name.encode()
            )
            if self.dll_handle
            else exec('raise ValueError("Invalid DLL handle")')
        )
        return (
            func
            if func
            else exec(f"raise OSError(\"Callback '{callback_name}' not found in DLL\")")
        )

    def set_windows_hook(self, callback_addr: int) -> None:
        user32, WH_GETMESSAGE = ctypes.windll.user32, 3
        HOOKPROC = ctypes.WINFUNCTYPE(
            ctypes.c_long, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM
        )

        user32.SetWindowsHookExA.argtypes = [
            ctypes.c_int,
            HOOKPROC,
            ctypes.wintypes.HMODULE,
            ctypes.wintypes.DWORD,
        ]
        user32.SetWindowsHookExA.restype = ctypes.wintypes.HHOOK

        self.hook = user32.SetWindowsHookExA(
            WH_GETMESSAGE,
            HOOKPROC(callback_addr),
            ctypes.wintypes.HMODULE(self.dll_handle),
            self._thread_id,
        )

        [
            exec(f'print(f"{err}")') if not cond else None
            for cond, err in [
                (
                    self.hook,
                    f"Windows hook failed with error {ctypes.windll.kernel32.GetLastError()}",
                ),
                (
                    ctypes.windll.user32.PostThreadMessageA(
                        self._thread_id, 0x0000, 0, 0
                    ),
                    f"PostThreadMessageA failed with error {ctypes.windll.kernel32.GetLastError()}",
                ),
            ]
        ]

    def release_handle(self) -> None:
        (
            ctypes.windll.kernel32.CloseHandle(self._handle),
            setattr(self, "_handle", 0),
        ) if self._handle else None

    @property
    def process_info(self) -> ProcessInfo:
        return self._process_info

    @property
    def active_handle(self) -> int:
        return self._handle

    @property
    def hwnd(self) -> int:
        return self._hwnd

    @property
    def thread_id(self) -> int:
        return self._thread_id
