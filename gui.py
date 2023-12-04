import customtkinter
from PIL import Image


class VisualizationFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.image = customtkinter.CTkImage(
            light_image=Image.open("Screenshot 2023-11-27 212549.png"),
            size=(
                Image.open("Screenshot 2023-11-27 212549.png").size[0] / 2,
                Image.open("Screenshot 2023-11-27 212549.png").size[1] / 2,
            ),
        )

        self.image_label = customtkinter.CTkLabel(self, image=self.image, text="")
        self.image_label.grid(row=0, column=0, sticky="nsew")


class MovementFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)


class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("ScytheArm Control Panel")
        self.geometry("1500x800")

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.visualization_frame = VisualizationFrame(self)
        self.visualization_frame.grid(
            row=0, column=0, padx=5, pady=5, columnspan=1, rowspan=1
        )

        self.movement_frame = MovementFrame(self)
        self.movement_frame.grid(
            row=1, column=0, sticky="nsew", padx=5, pady=5, rowspan=2
        )

        self.settings_frame = SettingsFrame(self)
        self.settings_frame.grid(
            row=0, column=1, sticky="nsew", padx=5, pady=5, rowspan=3, columnspan=3
        )


app = App()
app.mainloop()
