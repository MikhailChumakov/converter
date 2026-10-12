import customtkinter as ctk
from threading import Thread, Event
from config import load_config, save_config, select_folder
from watcher import watch_folder


def run_gui():
    ctk.set_appearance_mode("system")

    window = ctk.CTk()
    window.title("Converter")
    window.geometry("650x350")

    title = ctk.CTkLabel(
        window,
        text="Converter",
        font=("Arial", 24)
    )
    title.pack(pady=(20, 10))

    config = load_config()

    stop_event = Event()

    if config is not None:
        input_dir, output_dir = config  # распаковка кортежа с путями in и outs
    else:
        input_dir = None
        output_dir = None

    def change_input():
        nonlocal input_dir

        base_dir = select_folder()

        if base_dir is None:
            return

        input_dir = base_dir / "in"
        input_dir.mkdir(parents=True, exist_ok=True)

        if input_dir is not None:
            save_config(input_dir, output_dir)

        input_label.configure(text=f"IN: {input_dir}")


    def change_output():
        nonlocal output_dir

        base_dir = select_folder()

        if base_dir is None:
            return

        output_dir = base_dir / "out"
        output_dir.mkdir(parents=True, exist_ok=True)

        if output_dir is not None:
            save_config(input_dir, output_dir)

        output_label.configure(text=f"OUT: {output_dir}")


    def start_watcher():
        stop_event.clear()

        watcher_thread = Thread(
            target=watch_folder,
            args=(input_dir, output_dir, stop_event),
            daemon=True
        )

        watcher_thread.start()

        status.configure(text="Status: Watching")
        start_button.configure(state="disabled")
        stop_button.configure(state="normal")

        input_button.configure(state="disabled")
        output_button.configure(state="disabled")


    def stop_watcher():
        stop_event.set()

        status.configure(text="Status: Ready")
        start_button.configure(state="normal")
        stop_button.configure(state="disabled")

        input_button.configure(state="normal")
        output_button.configure(state="normal")


    # IN
    input_frame = ctk.CTkFrame(window)
    input_frame.pack(fill="x", padx=30, pady=5)

    input_label = ctk.CTkLabel(
        input_frame,
        text=f"IN: {input_dir}"
    )
    input_label.pack(side="left", padx=15, pady=10)

    input_button = ctk.CTkButton(
        input_frame,
        text="Change",
        width=80,
        command=change_input
    )
    input_button.pack(side="right", padx=15, pady=10)

    # OUT
    output_frame = ctk.CTkFrame(window)
    output_frame.pack(fill="x", padx=30, pady=5)

    output_label = ctk.CTkLabel(
        output_frame,
        text=f"OUT: {output_dir}"
    )
    output_label.pack(side="left", padx=15, pady=10)

    output_button = ctk.CTkButton(
        output_frame,
        text="Change",
        width=80,
        command=change_output
    )
    output_button.pack(side="right", padx=15, pady=10)

    status = ctk.CTkLabel(
        window,
        text="Status: Ready"
    )
    status.pack(pady=20)

    start_button = ctk.CTkButton(
        window,
        text="Start",
        command=start_watcher
    )
    start_button.pack(pady=10)

    stop_button = ctk.CTkButton(
        window,
        text="Stop",
        command=stop_watcher,
        state="disabled"
    )
    stop_button.pack(pady=5)

    window.mainloop()


if __name__ == "__main__":
    run_gui()
