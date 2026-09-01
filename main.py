import tkinter as tk
from tkinter import ttk, messagebox
from core import StorageManager, Note

class CryptaNoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CryptaNote - Secure Offline Vault")
        self.geometry("900x600")
        
        # Initialize storage engine
        self.storage = StorageManager()
        self.current_note_title = None

        self._build_menu()
        self._build_ui()
        self._bind_shortcuts()
        self.refresh_sidebar()

    def _build_menu(self):
        menubar = tk.Menu(self)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Note", command=self.new_note, accelerator="Ctrl+N")
        file_menu.add_command(label="Save Note", command=self.save_note, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Delete Note", command=self.delete_note)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.config(menu=menubar)

    def _build_ui(self):
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))

        # Left: Sidebar
        self.sidebar_frame = ttk.Frame(self.paned_window, width=250)
        self.paned_window.add(self.sidebar_frame, weight=1)

        self.note_listbox = tk.Listbox(self.sidebar_frame, font=("Segoe UI", 11), selectmode=tk.SINGLE)
        self.note_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.note_listbox.bind("<<ListboxSelect>>", self.on_note_select)

        scrollbar = ttk.Scrollbar(self.sidebar_frame, orient=tk.VERTICAL, command=self.note_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.note_listbox.config(yscrollcommand=scrollbar.set)

        # Right: Editor
        self.editor_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.editor_frame, weight=3)

        self.title_entry = ttk.Entry(self.editor_frame, font=("Segoe UI", 16, "bold"))
        self.title_entry.pack(fill=tk.X, pady=(0, 10))

        self.content_text = tk.Text(self.editor_frame, font=("Segoe UI", 12), wrap=tk.WORD, undo=True)
        self.content_text.pack(fill=tk.BOTH, expand=True)

        # Bottom Toolbar
        self.toolbar = ttk.Frame(self.editor_frame)
        self.toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(self.toolbar, text="New Note", command=self.new_note).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Save Note", command=self.save_note).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Delete Note", command=self.delete_note).pack(side=tk.LEFT, padx=2)

        # Bottom Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _bind_shortcuts(self):
        self.bind("<Control-n>", lambda event: self.new_note())
        self.bind("<Control-s>", lambda event: self.save_note())

    def refresh_sidebar(self):
        self.note_listbox.delete(0, tk.END)
        for title in sorted(self.storage.notes.keys()):
            self.note_listbox.insert(tk.END, title)

    def on_note_select(self, event):
        selection = self.note_listbox.curselection()
        if not selection:
            return
            
        title = self.note_listbox.get(selection[0])
        note = self.storage.notes.get(title)
        if note:
            self.current_note_title = title
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, note.title)
            
            self.content_text.delete("1.0", tk.END)
            self.content_text.insert(tk.END, note.content)
            self.status_var.set(f"Loaded note: {title}")

    def new_note(self):
        self.current_note_title = None
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)
        self.title_entry.focus_set()
        self.status_var.set("New note created")

    def save_note(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        
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
        self.status_var.set(f"Note '{title}' encrypted & saved.")

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
            self.status_var.set("Note deleted.")

if __name__ == "__main__":
    app = CryptaNoteApp()
    app.mainloop()