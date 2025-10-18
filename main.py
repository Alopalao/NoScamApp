import tkinter as tk
from tkinter import Tk, filedialog, messagebox, ttk
from tkinter import Event as TkEvent
from PIL import Image, ImageTk
from agent import Agent
from scam_handler import ScamAnalysisUIHandler, ScamAnalysisResult
from accordion import AccordionPanel

class Program:
    def __init__(self, screenSize):
        self.size = screenSize
        self.window = Tk(className="Scam Detector")
        self.window.geometry(self.size)
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(pady=5)
        self.analyzing_email = ""

        self.list_result = []

    def clean_screen(self):
        """Remove everything from application."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def main_page(self):
        """First page in the application"""
        self.name_label = tk.Label(self.main_frame, height=1, text="Scam Detector")
        self.name_label.pack(pady=5)

        self.name_label = tk.Label(self.main_frame, height=1, text="Insert the suspucios email:")
        self.name_label.pack(pady=5)

        # Input frame
        self.input_frame = tk.Frame(self.main_frame, width=800, height=300)
        self.input_frame.pack(pady=5)

        self.enter_email = tk.Text(self.input_frame, wrap=tk.WORD)
        enter_email_y = ttk.Scrollbar(self.input_frame, orient=tk.VERTICAL, command=self.enter_email.yview)

        self.enter_email.configure(yscrollcommand=enter_email_y.set)
        self.enter_email.grid(column=0, row=0)
        enter_email_y.grid(column=0, row=1)
        self.enter_email.insert(tk.END, "")

        # Analyze Button
        analyze = tk.Button(self.main_frame, text="Analyze email", command=self.analyze_email)
        analyze.pack(pady=5)

    def remove_result(self):
        for something in self.list_result:
            something.destroy()

    def analyze_email(self):
        agent = Agent()
        input_email = self.enter_email.get("1.0", tk.END)
        # Get text from self.enter_email
        result = agent.get_analysis(input_email)
        handler = ScamAnalysisUIHandler()
        result_data = handler.process_detection_result(result)
        self.remove_result()
        self.result_frame(result_data)

    def get_image_from_path(self, image_path: str):
        image = Image.open(image_path)
        image = image.resize((600, 300))
        return image

    def get_delete_email_png(self):
        """Return an image TK to be added to Label"""
        image_path = "images/delete_email.png"
        image = self.get_image_from_path(image_path)
        image_tk = ImageTk.PhotoImage(image)
        return image_tk

    def suggestion_window(self):
        self.clean_screen()

        frame = tk.Frame(self.main_frame)
        frame.pack(pady=5)
        result_text = tk.Label(frame, text="Next steps here.", wraplength=800)
        result_text.pack(pady=5)
        

        accordion_delete = AccordionPanel(frame, title="How to delete email messages?")
        accordion_delete.pack(pady=5)

        delete_frame = accordion_delete.get_content_frame()
        self.delete_image = self.get_delete_email_png()
        delete_image_frame = tk.Label(delete_frame, image=self.delete_image, borderwidth=5)
        delete_image_frame.pack(pady=5)

        back_button = tk.Button(frame, text="Analyze another email", command=self.start)
        back_button.pack(pady=5)


    def result_frame(self, result_data: ScamAnalysisResult):
        classification = result_data.classification
        risk_score = result_data.risk_score
        risk_level = result_data.risk_level
        color_code = result_data.color_code
        icon = result_data.icon

        message = result_data.user_friendly_message
        recommendations = result_data.recommendations

        result_frame = ttk.Frame(self.main_frame, padding="10")
        self.list_result.append(result_frame)
        result_frame.pack(pady=5)

        # --- 2. STATUS HEADER (Section 1) ---
        header_frame = tk.Frame(result_frame, bg=color_code)
        header_frame.pack(fill='x', pady=(0, 10))

        # ICON
        icon_label = tk.Label(header_frame, text=icon, font=('Helvetica', 30), fg='white', bg=color_code)
        icon_label.pack(side='left', padx=10, pady=5)

        # CLASSIFICATION
        class_label = tk.Label(header_frame, text=classification, font=('Helvetica', 24, 'bold'), fg='white', bg=color_code)
        class_label.pack(side='left', padx=10, pady=5)

        # --- 3. RISK DETAILS (Section 2) ---
        details_frame = ttk.Frame(result_frame)
        details_frame.pack(fill='x', pady=5)

        # RISK LEVEL & SCORE
        risk_text = f"Risk Level: {risk_level} (Score: {risk_score})"
        risk_label = ttk.Label(details_frame, text=risk_text, font=('Helvetica', 12, 'bold'))
        risk_label.pack(anchor='w', pady=(0, 5))

        # --- 4. USER-FRIENDLY MESSAGE (Section 3) ---
        message_label = ttk.Label(result_frame, text=message, wraplength=450, 
                                  font=('Helvetica', 11), justify='left')
        message_label.pack(fill='x', pady=(5, 10))

        # --- 5. RECOMMENDATIONS (Section 4) ---
        reco_title = ttk.Label(result_frame, text="Recommended Actions:", font=('Helvetica', 12, 'underline'))
        reco_title.pack(anchor='w', pady=(5, 5))

        # Use a Listbox for clear, line-by-line display
        reco_listbox = tk.Listbox(result_frame, height=len(recommendations), selectmode='none')
        for i, rec in enumerate(recommendations):
            reco_listbox.insert(i, rec)

        reco_listbox.pack(fill='x')

        next_button = tk.Button(self.main_frame, text="What to do next?", command=self.suggestion_window)
        next_button.pack(pady=5)
        self.list_result.append(next_button)


    def start(self):
        """Start application."""
        self.clean_screen()
        self.main_page()
        self.window.mainloop()


if __name__=='__main__':
    screenSize = "1000x1000"
    program = Program(screenSize)
    program.start()
