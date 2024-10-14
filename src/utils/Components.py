import tkinter as tk
import customtkinter as ctk
from typing import Callable, Optional


def create_labeled_entry(
    parent: tk.Widget, label_text: str, show: Optional[str] = None
) -> ctk.CTkEntry:
    """Creates a labeled entry widget.

    Args:
        parent (tk.Widget): The parent widget.
        label_text (str): The label text for the entry.
        show (Optional[str]): A character to show instead of the actual input (e.g., '*').

    Returns:
        ctk.CTkEntry: The created entry widget.
    """
    ctk.CTkLabel(parent, text=label_text).pack(pady=5)
    entry = ctk.CTkEntry(parent, show=show)
    entry.pack(pady=5)
    return entry


def create_button(parent: tk.Widget, text: str, command: Callable) -> ctk.CTkButton:
    """Creates a button widget.

    Args:
        parent (tk.Widget): The parent widget.
        text (str): The text displayed on the button.
        command (Callable): The function to be called when the button is clicked.

    Returns:
        ctk.CTkButton: The created button widget.
    """
    button = ctk.CTkButton(parent, text=text, command=command)
    button.pack(pady=10)
    return button


def create_textbox(
    parent: tk.Widget, height: int = 400, width: int = 500
) -> ctk.CTkTextbox:
    """Creates a read-only textbox.

    Args:
        parent (tk.Widget): The parent widget.
        height (int): The height of the textbox.
        width (int): The width of the textbox.

    Returns:
        ctk.CTkTextbox: The created textbox widget.
    """
    text_box = ctk.CTkTextbox(parent, height=height, width=width)
    text_box.pack(pady=10)
    text_box.configure(state=tk.DISABLED)
    return text_box


def clear_textbox(text_box: ctk.CTkTextbox) -> None:
    """Clears the content of a textbox.

    Args:
        text_box (ctk.CTkTextbox): The textbox to be cleared.
    """
    text_box.configure(state=tk.NORMAL)
    text_box.delete(1.0, tk.END)
    text_box.configure(state=tk.DISABLED)


def update_textbox(text_box: ctk.CTkTextbox, text: str) -> None:
    """Updates the content of a textbox.

    Args:
        text_box (ctk.CTkTextbox): The textbox to be updated.
        text (str): The new text to insert into the textbox.
    """
    text_box.configure(state=tk.NORMAL)
    text_box.delete(1.0, tk.END)
    text_box.insert(tk.END, text)
    text_box.configure(state=tk.DISABLED)


def create_scrollable_frame(parent: tk.Widget) -> ctk.CTkFrame:
    """Creates a frame with a vertical scrollbar.

    Args:
        parent (tk.Widget): The parent widget.

    Returns:
        ctk.CTkFrame: The created scrollable frame.
    """
    try:
        canvas = ctk.CTkCanvas(parent)
        scrollbar = ctk.CTkScrollbar(
            parent, orientation="vertical", command=canvas.yview
        )
        scrollable_frame = ctk.CTkFrame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scrollable_frame
    except Exception as e:
        print(f"Error creating scrollable frame: {e}")
        return None
