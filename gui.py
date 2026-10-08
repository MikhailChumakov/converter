import customtkinter as ctk
from config import load_config


def run_gui():
    ctk.set_appearance_mode("system")

    window = ctk.CTk()

    window.title("Converter")
    window.geometry("650x300")

    title = ctk.CTkLabel(
        window,
        text="Converter",
        font=("Arial", 24)
    )
    title.pack(pady=(30, 20))

    config = load_config()

    if config is not None:
        input_dir, output_dir = config  # распаковка кортежа с путями in и outs
    else:
        input_dir = "Not selected"
        output_dir = "Not selected"

    input_label = ctk.CTkLabel(
        window,
        text=f"IN: {input_dir}"
    )
    input_label.pack(pady=10)

    output_label = ctk.CTkLabel(
        window,
        text=f"OUT: {output_dir}"
    )
    output_label.pack(pady=10)

    status = ctk.CTkLabel(
        window,
        text="Status: Ready"
    )
    status.pack(pady=20)

    window.mainloop()


if __name__ == "__main__":
    run_gui()
