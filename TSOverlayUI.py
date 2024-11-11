# import ctypes
import tkinter as tk

from wrapper.TSClient import TSClient


class TSOverlayUI:
    def __init__(self):
        # Initialize the main window
        self.root = tk.Tk()
        self.root.attributes('-topmost', True)  # Keep the window on top
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.geometry("100x100+10+10")  # Position at top-left, adjust size as needed

        # Make the background transparent
        # self.root.wm_attributes('-transparentcolor', self.root['bg'])
        self.root.wm_attributes("-transparentcolor", "white")
        # Set an alpha value (0.0 for completely transparent, 1.0 for completely opaque)
        self.root.wm_attributes("-alpha", 1.0)  # 70% opacity

        self.frame = tk.Frame(self.root, background="white")
        self.frame.pack(fill=tk.BOTH, expand=1)

        # Make the window click-through
        # self.make_click_through()

        # Dictionary to hold labels for each name
        self.labels = {}

    # def make_click_through(self):
    #     hwnd = ctypes.windll.user32.GetForegroundWindow()
    #     if hwnd != self.root.winfo_id():
    #         ctypes.windll.user32.SetForegroundWindow(self.root.winfo_id())
    #
    #     # Get system metrics for layered windows
    #     LWA_COLORKEY = 0x00000001
    #     LWA_ALPHA = 0x00000002
    #     GWL_EXSTYLE = -20
    #     WS_EX_LAYERED = 0x00080000
    #     WS_EX_TRANSPARENT = 0x00000020
    #
    #     # Set layered style
    #     ctypes.windll.user32.SetWindowLongW(
    #         self.root.winfo_id(),
    #         GWL_EXSTYLE,
    #         ctypes.windll.user32.GetWindowLongW(self.root.winfo_id(),GWL_EXSTYLE) | WS_EX_LAYERED | WS_EX_TRANSPARENT
    #     )
    #
    #     # Set window to be transparent to mouse and keyboard events
    #     ctypes.windll.user32.SetLayeredWindowAttributes(self.root.winfo_id(), 0, 255, LWA_ALPHA)

    def clear_clients(self):
        keyLabels = self.labels.keys()
        for label in keyLabels:
            self.labels[label].destroy()
            del self.labels[label]
        self.updateSize()

    def add_client(self, client: TSClient):
        background = "#A0A0A0"
        if client.commander:
            background = "#F19E39"
        if client.whispering:
            background = "#EA33F7"
        key = str(client.connectionId) + '_' + str(client.clientId)
        if key in self.labels.keys():
            self.labels[key].setvar("background", background)
        else:
                # label = tk.Label(self.frame, text=client.name, compound=tk.LEFT, background="white")
                label = tk.Label(
                    self.frame,
                    text = client.name,
                    compound = tk.LEFT,
                    background = background,  # Semi-transparent gray background
                    foreground = "black",  # White text color
                    font = ("Helvetica", 12, "bold"),  # Bold font for better visibility
                    # relief = "raised",  # Raised border around the text
                    # borderwidth = 2  # Width of the border
                )
                label.pack(anchor="w")
                self.labels[key] = label
                self.updateSize()

    def remove_client(self, client: TSClient):
        key = str(client.connectionId) + '_' + str(client.clientId)
        if key in self.labels.keys():
            self.labels[key].destroy()
            del self.labels[key]
            self.updateSize()

    def updateSize(self):
        # Update window size to fit content
        self.root.update_idletasks()
        if len(self.labels) > 0:
            # Calculate the maximum width needed
            width = max(label.winfo_reqwidth() for label in self.labels.values()) if self.labels else 1
            # Calculate the total height needed
            height = sum(label.winfo_reqheight() for label in self.labels.values()) if self.labels else 1
        else:
            width = 1
            height = 1
        # Set new geometry of the window
        self.root.geometry(f"{width}x{height}")

    def run(self):
        # This method keeps the window running
        self.root.mainloop()