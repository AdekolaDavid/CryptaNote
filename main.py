import customtkinter as ctk
from tkinter import messagebox
from core import StorageManager, Note

# Set up overall appearance theme defaults
ctk.set_appearance_mode("System")  # Follows system theme or can be "Dark"/"Light"
ctk.set_default_color_theme("blue")

class CryptaNoteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CryptaNote - Secure Offline Vault")
        self.geometry("950x600")
        
        # Initialize storage engine
        self.storage = StorageManager()
        self.current_note_title = None

        self._build_ui()
        self._bind_shortcuts()
        self.refresh_sidebar()

    def _build_ui(self):
        # Configure grid weight for responsiveness
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        # Sidebar Header / Search-ready placeholder
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🔒 CryptaNote", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # New Note Button in Sidebar for quick access
        self.sidebar_new_btn = ctk.CTkButton(
            self.sidebar_frame, 
            text="+ New Note", 
            command=self.new_note,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.sidebar_new_btn.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Scrollable container for notes list (replaces old native listbox)
        self.notes_scroll_frame = ctk.CTkScrollableFrame(self.sidebar_frame, label_text="Your Notes")
        self.notes_scroll_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.notes_scroll_frame.grid_columnconfigure(0, weight=1)

        # Theme Switcher at bottom of sidebar
        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["System", "Light", "Dark"],
            command=self.change_appearance_mode
        )
        self.theme_menu.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.theme_menu.set("System")

        # Right Editor Workspace Frame
        self.editor_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.editor_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(2, weight=1)

        # Title Input Entry
        self.title_entry = ctk.CTkEntry(
            self.editor_frame, 
            placeholder_text="Note Title...", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            height=45
        )
        self.title_entry.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Toolbar Frame (Placed right below title for clean ergonomics)
        self.toolbar_frame = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        self.toolbar_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.save_btn = ctk.CTkButton(self.toolbar_frame, text="Save Note", command=self.save_note, width=100)
        self.save_btn.pack(side="left", padx=(0, 8))

        self.delete_btn = ctk.CTkButton(
            self.toolbar_frame, 
            text="Delete", 
            command=self.delete_note, 
            fg_color="#c92a2a", 
            hover_color="#a61e1e", 
            width=90
        )
        self.delete_btn.pack(side="left")

        # Rich Content Text Box
        self.content_text = ctk.CTkTextbox(
            self.editor_frame, 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            corner_radius=6,
            undo=True
        )
        self.content_text.grid(row=2, column=0, sticky="nsew")

        # Status Bar Tracker
        self.status_label = ctk.CTkLabel(
            self.editor_frame, 
            text="Ready", 
            font=ctk.CTkFont(family="Segoe UI", size=11), 
            text_color="gray"
        )
        self.status_label.grid(row=3, column=0, sticky="w", pady=(8, 0))

    def _bind_shortcuts(self):
        self.bind("<Control-n>", lambda event: self.new_note())
        self.bind("<Control-s>", lambda event: self.save_note())

    def change_appearance_mode(self, new_theme: str):
        ctk.set_appearance_mode(new_theme)
        self.status_label.configure(text=f"Theme set to {new_theme}")

    def refresh_sidebar(self):
        # Clear existing note buttons in scroll frame
        for widget in self.notes_scroll_frame.winfo_children():
            widget.destroy()

        # Populate with modern note buttons
        for index, title in enumerate(sorted(self.storage.notes.keys())):
            btn = ctk.CTkButton(
                self.notes_scroll_frame,
                text=title,
                anchor="w",
                fg_color="transparent",
                text_color=("black", "white"),
                hover_color=("#e2e8f0", "#2b2b2b"),
                command=lambda t=title: self.load_note_by_title(t)
            )
            btn.grid(row=index, column=0, sticky="ew", pady=2)

    def load_note_by_title(self, title):
        note = self.storage.notes.get(title)
        if note:
            self.current_note_title = title
            self.title_entry.delete(0, "end")
            self.title_entry.insert(0, note.title)
            
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", note.content)
            self.status_label.configure(text=f"Loaded note: {title}")

    def new_note(self):
        self.current_note_title = None
        self.title_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
        self.title_entry.focus()
        self.status_label.configure(text="New note created")

    def save_note(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", "end-1c").strip()
        
        if not title:
            messagebox.showwarning("Warning", "Note title cannot be empty.")
            return

        if self.current_note_title and self.current_note_title != title:
            if self.current_note_title in self.storage.notes:
                del self.storage.notes[self.current_note_title]

        if title in self.storage.notes:
            self.storage.notes[title].update_content(content)
        else:
            self.storage.notes[title] = Note(title=title, content=content)

        self.storage.save_notes()
        self.current_note_title = title
        self.refresh_sidebar()
        self.status_label.configure(text=f"Note '{title}' encrypted & saved securely.")

    def delete_note(self):
        if not self.current_note_title or self.current_note_title not in self.storage.notes:
            messagebox.showwarning("Warning", "No active note selected to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{self.current_note_title}'?")
        if confirm:
            del self.storage.notes[self.current_note_title]
            self.storage.save_notes()
            self.new_note()
            self.refresh_sidebar()
            self.status_label.configure(text="Note deleted.")

if __name__ == "__main__":
    app = CryptaNoteApp()
    app.mainloop()