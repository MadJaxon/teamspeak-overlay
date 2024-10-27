import ctypes
import threading

from TSOverlay import TSOverlay
from TSOverlayUI import TSOverlayUI


if __name__ == "__main__":
    # ctypes.windll.user32.SetProcessDPIAware()

    overlay = TSOverlay()
    ui = TSOverlayUI()

    # Start the WebSocket in a separate thread
    websocket_thread = threading.Thread(target=overlay.start, args=(ui,))
    websocket_thread.start()

    # Start the GUI
    ui.run()