from .windows.winfunc import WinFunc
from colorama import Fore, init


import time

init(autoreset=True, convert=True, strip=True)


class Injector:
    def __init__(self) -> None:
        self.win = WinFunc()

    def inject(self, hook_name: str, dll_path: str) -> None:
        [
            step()
            for step in [
                self._setup_process,
                self._setup_window,
                lambda: self._setup_hook(hook_name, dll_path),
            ]
        ]

    def _setup_process(self) -> None:
        self.win.set_process_by_name("RobloxPlayerBeta.exe")
        handle = self.win.acquire_handle()
        [
            self._print_status(s, c, m)
            for s, c, m in [
                (
                    "+",
                    Fore.BLUE,
                    f"Process: {self.win.process_info.name} ({Fore.GREEN}{self.win.process_info.id}{Fore.RESET})",
                ),
                ("+", Fore.BLUE, f"Process Handle: {handle}"),
            ]
        ]

    def _setup_window(self) -> None:
        self.win.acquire_window_info()
        [
            self._print_status(s, c, m)
            for s, c, m in [
                ("-", Fore.YELLOW, "Looking for Roblox window..."),
                ("+", Fore.BLUE, f"Window Handle: {self.win.hwnd}"),
                ("+", Fore.BLUE, f"Thread ID: {self.win.thread_id}"),
            ]
        ]

    def _setup_hook(self, hook_name: str, dll_path: str) -> None:
        (self.win.handle, self.win.callback_address) = (
            self.win.load_dll(dll_path),
            self.win.get_callback_address(hook_name),
        )

        [
            self._print_status(s, c, m)
            for s, c, m in [
                ("+", Fore.BLUE, f"DLL Handle: {self.win.handle}"),
                ("+", Fore.BLUE, f"Callback Address: {self.win.callback_address}"),
            ]
        ]
        self.win.set_windows_hook(self.win.callback_address)
        [
            self._print_status(s, c, m)
            for s, c, m in [("+", Fore.BLUE, "Hook set successfully")]
        ]
        time.sleep(400)

    def _print_status(self, s: str, c: str, m: str) -> None:
        print(f"[{c}{s}{Fore.RESET}] {m}")


if __name__ == "__main__":
    Injector().inject()
