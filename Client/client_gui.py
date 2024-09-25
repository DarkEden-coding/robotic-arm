from threading import Thread

import customtkinter as ctk
from PIL import Image

from client_backend import get_server_logs, send_command, get_log


class RenderedView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        placeholder_image = ctk.CTkImage(Image.open("placeholder.png"), size=(150, 150))
        self.display_label = ctk.CTkLabel(
            self,
            image=placeholder_image,
            text="",
            anchor="center",
        )
        self.display_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)


class NumericalInputAndDisplayFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        def make_position_frame(place_holder_text):
            position_frame = ctk.CTkFrame(self)
            position_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
            position_frame.grid_columnconfigure(0, weight=1)
            position_frame.grid_rowconfigure(0, weight=1)
            position_frame.grid_rowconfigure(1, weight=1)
            position_label = ctk.CTkLabel(position_frame, text="0.0", anchor="center")
            position_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))
            position_entry = ctk.CTkEntry(
                position_frame, placeholder_text=place_holder_text
            )
            position_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
            return position_frame

        self.grid_columnconfigure([i for i in range(4)], weight=1, uniform="4")
        self.grid_rowconfigure(0, weight=1)

        self.position_x_frame = make_position_frame("X")
        self.position_x_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.position_y_frame = make_position_frame("Y")
        self.position_y_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        self.position_z_frame = make_position_frame("Z")
        self.position_z_frame.grid(row=0, column=2, sticky="ew", padx=10, pady=10)

        self.position_roll_frame = make_position_frame("Y Rotation")
        self.position_roll_frame.grid(row=0, column=3, sticky="ew", padx=10, pady=10)

        self.position_pitch_frame = make_position_frame("Z Rotation")
        self.position_pitch_frame.grid(row=0, column=4, sticky="ew", padx=10, pady=10)


class SpeedStartStopFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1, uniform="3")
        self.grid_columnconfigure(1, weight=1, uniform="3")
        self.grid_rowconfigure(0, weight=1)

        self.speed_frame = ctk.CTkFrame(self)
        self.speed_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.speed_frame.grid_columnconfigure(0, weight=1, uniform="2")
        self.speed_frame.grid_columnconfigure(1, weight=1, uniform="2")
        self.speed_frame.grid_rowconfigure(0, weight=1)

        self.speed_slider = ctk.CTkSlider(self.speed_frame, from_=0, to=100)
        self.speed_slider.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.speed_entry = ctk.CTkEntry(self.speed_frame, placeholder_text="Speed")
        self.speed_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.startup_button = ctk.CTkButton(self.button_frame, text="Start")
        self.startup_button.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.emergency_stop_button = ctk.CTkButton(
            self.button_frame, text="Emergency Stop", fg_color="red"
        )
        self.emergency_stop_button.grid(row=0, column=1, sticky="ew", padx=10, pady=10)


class SystemButtonFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure([i for i in range(4)], weight=1, uniform="1")
        self.grid_rowconfigure(0, weight=1)

        self.theme_button = ctk.CTkButton(
            self, text="Toggle Theme", command=toggle_theme
        )
        self.theme_button.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.exit_button = ctk.CTkButton(
            self, text="Exit", command=parent.parent.on_close
        )
        self.exit_button.grid(row=0, column=4, sticky="ew", padx=10, pady=10)


# Define the Left Frame class
class LeftFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure([i for i in range(6)], weight=1, uniform="1")

        self.rendered_view = RenderedView(self)
        self.rendered_view.grid(
            row=0, column=0, sticky="nsew", padx=10, pady=10, rowspan=3
        )

        self.numerical_input_and_display_frame = NumericalInputAndDisplayFrame(self)
        self.numerical_input_and_display_frame.grid(
            row=3, column=0, sticky="ew", padx=10, pady=5
        )

        self.speed_start_stop_frame = SpeedStartStopFrame(self)
        self.speed_start_stop_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)

        self.theme_frame = SystemButtonFrame(self)
        self.theme_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=10)


# Define the Client Input Frame class
class ClientInputFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.client_input = ctk.CTkEntry(self, placeholder_text="Enter command")
        self.client_input.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        self.send_button = ctk.CTkButton(self, text="Send", command=self.send_command)
        self.send_button.grid(row=1, column=1, sticky="ew", padx=10, pady=10)

    def send_command(self):
        command = self.client_input.get()
        self.client_input.delete(0, "end")
        Thread(target=send_command, args=(command,)).start()


# Define the Right Frame class
class RightFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=2)

        self.client_console = ctk.CTkTextbox(self, wrap="word")
        self.client_console.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))
        self.client_console.insert("0.0", "Client logs will appear here.")
        self.client_console.configure(state="disabled")

        self.client_input_frame = ClientInputFrame(self)
        self.client_input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        self.server_console = ctk.CTkTextbox(self, wrap="word")
        self.server_console.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.server_console.insert("0.0", "Server logs will appear here.")
        self.server_console.configure(state="disabled")


# Define the main GUI class
def toggle_theme():
    # Switch between light and dark mode
    if ctk.get_appearance_mode() == "Light":
        ctk.set_appearance_mode("Dark")
    else:
        ctk.set_appearance_mode("Light")


class RoboticArmControlApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Robotic Arm Control")
        self.geometry("1400x700")  # Default large window size
        self.resizable(False, False)

        # Configure grid for responsive layout
        self.grid_columnconfigure(0, weight=1, uniform="5")  # Left frame
        self.grid_columnconfigure(1, weight=1, uniform="5")  # Right frame
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = LeftFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)

        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.periodic_update()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        print("Closing...")
        self.quit()

    def periodic_update(self):
        self.right_frame.server_console.configure(state="normal")
        self.right_frame.server_console.delete("0.0", "end")
        self.right_frame.server_console.insert("0.0", get_server_logs().get("data"))
        self.right_frame.server_console.update_idletasks()
        self.right_frame.server_console.configure(state="disabled")

        self.right_frame.client_console.configure(state="normal")
        self.right_frame.client_console.delete("0.0", "end")
        self.right_frame.client_console.insert("0.0", get_log())
        self.right_frame.client_console.update_idletasks()
        self.right_frame.client_console.configure(state="disabled")

        self.after(10, self.periodic_update)


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")  # or "Light"
    ctk.set_default_color_theme("blue")

    app = RoboticArmControlApp()
    app.mainloop()
