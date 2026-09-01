# Secure Notes Application – Development Specification

## Project Overview
Create a **desktop application** for storing encrypted text notes with a graphical user interface.  
**Target:** Python 3.8+  
**Main libraries:** `tkinter` (built-in), `cryptography` (for AES‑256 encryption)  
**All data** must be stored locally, encrypted at rest. No network communication.

---

## Functional Requirements

### Core Features
- **Create** a new note with a title and content.
- **Read** existing notes by selecting from a list.
- **Update** (edit and save) any note.
- **Delete** notes with confirmation.
- **Search** notes by title or content (case-insensitive).
- **Export** all notes as an encrypted backup (timestamped file).
- **Import** an encrypted backup file to restore notes.

### User Interface
- **Sidebar:** List of note titles (sorted alphabetically) with a scrollbar.
- **Editor:** Title entry field and a multi-line text area for content.
- **Status bar:** Show current status (e.g., "Ready", "Note saved", search results).
- **Menu bar:** File, Edit, View, Help with shortcuts.
- **Toolbar buttons** for quick actions: New, Save, Delete, Search, Export.
- **Timestamp display** showing creation and last update time for the current note.

### Keyboard Shortcuts
- `Ctrl+N` – New note  
- `Ctrl+S` – Save note  
- `Ctrl+F` – Search notes  
- `Ctrl+O` – Export backup  
- `Esc` – Clear search / deselect  
- `Double-click` on a note → quick edit (focus on content)

### Additional Features
- **Dark/Light theme toggle** (View menu).
- **Word wrap toggle** (View menu).
- **Auto-save** on window close (prompt if changes are unsaved).
- **Undo/Redo** support in the text editor (using tkinter’s built-in undo).

---

## Non‑Functional Requirements
- **Security:** All notes are encrypted using AES‑256 (Fernet symmetric encryption).
- **Portability:** All user data resides in `~/.secure_notes/` (or `%USERPROFILE%\.secure_notes` on Windows).
- **Offline:** No internet connection required.
- **Performance:** Instant load/save even with hundreds of notes.
- **Error handling:** Graceful failure with user‑friendly messages.

---

## Technical Architecture

### Technology Stack
| Component       | Choice                        |
|-----------------|-------------------------------|
| Language        | Python 3.8+                   |
| GUI Framework   | Tkinter (with ttk extensions) |
| Encryption      | `cryptography.fernet.Fernet`  |
| Data Storage    | JSON file encrypted on disk   |
| Key Management  | Generate key on first run; store in separate file |

### Module Breakdown (single file for simplicity)

1. **Config & Constants**  
   – App name, version, data directory paths, window size.

2. **Data Model (`Note` class)**  
   – Attributes: `title`, `content`, `created_at`, `updated_at` (ISO datetime strings).  
   – Methods: `to_dict()`, `from_dict()`, `update_content()`, `get_formatted_time()`.

3. **Encryption Manager (`EncryptionManager`)**  
   – `__init__()`: load existing key or generate a new one, store in `DATA_DIR/key.key`.  
   – `encrypt(data)` → bytes  
   – `decrypt(data)` → str

4. **Storage Manager (`StorageManager`)**  
   – `__init__()`: load encrypted `notes.json` via encryption manager.  
   – `load_notes()`: decrypt and parse JSON into a dict of `Note` objects.  
   – `save_notes()`: serialize dict to JSON, encrypt, write to disk.  
   – `add_note(note)`, `delete_note(title)`, `get_note(title)`, `list_titles()`, `search_notes(query)`, `export_backup()`, `import_backup()`.

5. **GUI Application (`SecureNotesApp`)**  
   – Inherits from `tk.Tk` or uses a root window.  
   – Builds the main layout using `PanedWindow`, `Listbox`, `ScrolledText`, etc.  
   – Handles all user interactions and event callbacks.  
   – Updates status bar and note list dynamically.

### Data Flow Diagram