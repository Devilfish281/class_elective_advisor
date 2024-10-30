# ui/gui.py

import tkinter as tk
from tkinter import ttk

from ai_integration.ai_module import get_recommendations


def main_int_ui():
    """
    Initialize the User Interface for the Smart Elective Advisor.

    This function sets up the main UI window with input fields for user preferences,
    a button to get recommendations, and a text area to display the output.
    """
    print("Initializing UI...")
    root = tk.Tk()
    root.title("Smart Elective Advisor")
    root.geometry("800x600")

    # Create a frame for input
    input_frame = ttk.Frame(root, padding="10")
    input_frame.pack(fill=tk.X)

    ttk.Label(input_frame, text="Enter Your Preferences:").pack(
        side=tk.LEFT, padx=(0, 10)
    )
    preferences_entry = ttk.Entry(input_frame, width=50)
    preferences_entry.pack(side=tk.LEFT, padx=(0, 10))

    def on_submit():
        """
        Handle the submission of user preferences.

        This function retrieves the user preferences from the input field, passes them to
        the AI model to get recommendations, and displays the result in the output text widget.
        """
        prefs = preferences_entry.get()
        recommendations = get_recommendations(prefs)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, recommendations)

    submit_button = ttk.Button(
        input_frame, text="Get Recommendations", command=on_submit
    )
    submit_button.pack(side=tk.LEFT)

    # Create a text widget to display recommendations
    output_frame = ttk.Frame(root, padding="10")
    output_frame.pack(fill=tk.BOTH, expand=True)

    output_text = tk.Text(output_frame, wrap=tk.WORD)
    output_text.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
    print("UI Closed.")
