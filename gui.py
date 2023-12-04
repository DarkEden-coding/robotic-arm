import customtkinter
from PIL import Image
from client import setup, enable_motors, disable_motors, shutdown, set_percent_speed, move, emergency_stop, \
    close_connection, get_position
from threading import Thread

print("Starting GUI and setting up connection to server...")

setup()

print("Connection to server established.")


def threaded_tasks():
    while True:
        app.movement_frame.update_actual_coordinates()


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

        self.columnconfigure((0, 1, 2), weight=1)

        self.coordinates_label = customtkinter.CTkLabel(self, text="Coordinates")
        self.coordinates_label.grid(row=0, column=0)

        self.emergency_stop_button = customtkinter.CTkButton(self, text="Emergency Stop", fg_color="red",
                                                             command=emergency_stop)
        self.emergency_stop_button.grid(row=0, column=2, pady=5)

        self.actual_x_label = customtkinter.CTkLabel(self, text="Actual X")
        self.actual_x_label.grid(row=1, column=0)

        self.actual_y_label = customtkinter.CTkLabel(self, text="Actual Y")
        self.actual_y_label.grid(row=1, column=1)

        self.actual_z_label = customtkinter.CTkLabel(self, text="Actual Z")
        self.actual_z_label.grid(row=1, column=2)

        self.actual_x_entry = customtkinter.CTkEntry(self)
        self.actual_x_entry.grid(row=2, column=0)

        self.actual_y_entry = customtkinter.CTkEntry(self)
        self.actual_y_entry.grid(row=2, column=1)

        self.actual_z_entry = customtkinter.CTkEntry(self)
        self.actual_z_entry.grid(row=2, column=2)

        self.actual_x_entry.configure(state="disabled")
        self.actual_y_entry.configure(state="disabled")
        self.actual_z_entry.configure(state="disabled")

        self.target_x_label = customtkinter.CTkLabel(self, text="Target X")
        self.target_x_label.grid(row=3, column=0)

        self.target_y_label = customtkinter.CTkLabel(self, text="Target Y")
        self.target_y_label.grid(row=3, column=1)

        self.target_z_label = customtkinter.CTkLabel(self, text="Target Z")
        self.target_z_label.grid(row=3, column=2)

        self.target_x_entry = customtkinter.CTkEntry(self)
        self.target_x_entry.grid(row=4, column=0)

        self.target_y_entry = customtkinter.CTkEntry(self)
        self.target_y_entry.grid(row=4, column=1)

        self.target_z_entry = customtkinter.CTkEntry(self)
        self.target_z_entry.grid(row=4, column=2)

        self.enable_motors_button = customtkinter.CTkButton(self, text="Enable Motors", command=enable_motors)
        self.enable_motors_button.grid(row=5, column=0, pady=5)

        self.disable_motors_button = customtkinter.CTkButton(
            self, text="Disable Motors", command=disable_motors
        )
        self.disable_motors_button.grid(row=5, column=2, pady=5)

        self.speed_label = customtkinter.CTkLabel(self, text="Speed")
        self.speed_label.grid(row=6, column=1)

        self.speed_value_label = customtkinter.CTkLabel(self, text="100 %")
        self.speed_value_label.grid(row=6, column=2)

        self.speed_slider = customtkinter.CTkSlider(
            self,
            from_=10,
            to=200,
            command=self.update_speed_label,
            number_of_steps=190,
        )
        self.speed_slider.grid(row=7, column=0, columnspan=3, sticky="nsew")

        self.move_to_target_button = customtkinter.CTkButton(
            self, text="Move to Target", command=self.move_to_target
        )
        self.move_to_target_button.grid(row=0, column=1)

        self.update_speed_button = customtkinter.CTkButton(self, text="Update Speed", command=self.change_speed)
        self.update_speed_button.grid(row=8, column=1, pady=5)

        self.shutdown_button = customtkinter.CTkButton(self, text="Shutdown", fg_color="red", command=shutdown)
        self.shutdown_button.grid(row=8, column=2, pady=5)

    def update_speed_label(self, value):
        self.speed_value_label.configure(text=f"{round(value)} %")

    def update_actual_coordinates(self):
        self.actual_x_entry.configure(text=get_position()[0])
        self.actual_y_entry.configure(text=get_position()[1])
        self.actual_z_entry.configure(text=get_position()[2])

    def change_speed(self):
        set_percent_speed(self.speed_slider.get() / 100)

    def move_to_target(self):
        move((self.target_x_entry.get(), self.target_y_entry.get(), self.target_z_entry.get()))


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

        self.threaded_tasks_thread = Thread(target=threaded_tasks)
        self.threaded_tasks_thread.start()


app = App()
app.mainloop()

close_connection()
