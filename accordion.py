import tkinter as tk

class AccordionPanel(tk.Frame):
    """A reusable, collapsible panel widget."""
    def __init__(self, master, title="Section Title", **kwargs):
        super().__init__(master, **kwargs)
        
        self.title = title
        
        # --- 1. Header/Toggle Button ---
        # A frame to hold the button and ensure it spans the width
        header_frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        header_frame.pack(fill='x')

        self.toggle_button = tk.Button(
            header_frame,
            text=f"{self.title} +",
            command=self.toggle,
            font=('Arial', 10, 'bold'),
            anchor='w' # Align text to the left
        )
        self.toggle_button.pack(fill='x', padx=5, pady=5)

        # --- 2. Collapsible Content Frame ---
        # This is where the user will place their widgets
        self.content_frame = tk.Frame(self, bg='#f0f0f0', borderwidth=1, relief=tk.SUNKEN)
        
        # Start in the collapsed state (do not pack the content_frame)
        self.is_expanded = False

    def get_content_frame(self):
        """
        Returns the inner frame where the user can place widgets.
        """
        return self.content_frame

    def toggle(self):
        """
        Switches the panel between expanded and collapsed states.
        """
        if self.is_expanded:
            # Collapse the panel
            self.content_frame.pack_forget()
            self.toggle_button.config(text=f"{self.title} +")
            self.is_expanded = False
        else:
            # Expand the panel
            # Use fill='both' and expand=True to make it dynamic
            self.content_frame.pack(fill='both', expand=True, padx=2, pady=2)
            self.toggle_button.config(text=f"{self.title} -")
            self.is_expanded = True
