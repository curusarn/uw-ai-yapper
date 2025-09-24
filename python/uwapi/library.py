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
        try:
            print("Reading bots.h...", flush=True)
            api_def = open(
                os.path.join(os.path.split(os.path.abspath(__file__))[0], "bots.h"), "r"
            ).read()

            steam_path = os.path.expanduser(self.library_path())
            print("looking for uw library in: " + steam_path, flush=True)

            print("Changing to library directory...", flush=True)
            os.chdir(steam_path)

            print("Creating FFI instance...", flush=True)
            self._ffi = FFI()

            print("Defining C API...", flush=True)
            self._ffi.cdef(api_def)

            library_file = os.path.join(steam_path, self.library_name())
            print(f"Loading library: {library_file}", flush=True)
            self._api = self._ffi.dlopen(library_file)

            print("Initializing interop...", flush=True)
            uw_interop.initialize(self._ffi, self._api)

            print(f"Calling uwInitialize with version: {self._api.UW_VERSION}", flush=True)
            uw_interop.uwInitialize(self._api.UW_VERSION)  # type: ignore

            print("Initializing console logger...", flush=True)
            uw_interop.uwInitializeConsoleLogger()

            print("Initializing events...", flush=True)
            uw_events.initialize()

            print("UwapiLibrary initialization complete!", flush=True)
        except Exception as e:
            print(f"UwapiLibrary initialization failed: {e}", flush=True)
            print(f"Exception type: {type(e).__name__}", flush=True)
            import traceback
            traceback.print_exc()
            raise

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
