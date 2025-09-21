import os
import sys
from cffi import FFI
from .interop import *
from .events import uw_events


class UwapiLibrary:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._ffi = None
        self._api = None

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.dispose()

    def initialize(self) -> None:
        api_def = open(
            os.path.join(os.path.split(os.path.abspath(__file__))[0], "bots.h"), "r"
        ).read()

        steam_path = os.path.expanduser(self.library_path())
        print("looking for uw library in: " + steam_path, flush=True)
        os.chdir(steam_path)

        self._ffi = FFI()
        self._ffi.cdef(api_def)
        self._api = self._ffi.dlopen(os.path.join(steam_path, self.library_name()))

        uw_interop.initialize(self._ffi, self._api)
        uw_interop.uwInitialize(self._api.UW_VERSION)  # type: ignore
        uw_interop.uwInitializeConsoleLogger()
        uw_events.initialize()

    def dispose(self) -> None:
        uw_interop.uwDeinitialize()

        # attempting graceful closing causes the process to hung somewhere in steam shutdown code
        # we will instead terminate the process, skipping most of python's clean-up code
        print("terminating the process")
        os._exit(0)  # this is considered a success

        # print("disposing of uwapi library")
        # self._ffi = None
        # self._api = None
        # uw_interop.initialize(self._ffi, self._api)

    def library_path(self) -> str:
        steam_path = os.environ.get("UNNATURAL_ROOT", "")
        if steam_path != "":
            return steam_path
        if sys.platform == "win32":
            return "C:/Program Files (x86)/Steam/steamapps/common/Unnatural Worlds/bin"
        return "~/.steam/steam/steamapps/common/Unnatural Worlds/bin"

    def library_name(self) -> str:
        return "{}unnatural-uwapi{}.{}".format(
            "" if sys.platform == "win32" else "lib",
            "-hard" if __debug__ else "",
            "dll" if sys.platform == "win32" else "so",
        )
