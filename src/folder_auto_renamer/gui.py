"""Tkinter Graphical User Interface for Auto Folder Renamer Pro."""

import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional

from folder_auto_renamer.config import (
    DuplicateStrategy,
    RenameMode,
    RenamerConfig,
    SortOrder,
)
from folder_auto_renamer.renamer import FolderRenamer
from folder_auto_renamer.undo import UndoManager


class RenamerGUI(tk.Tk):
    """Main desktop application window for Auto Folder Renamer Pro."""

    def __init__(self) -> None:
        """Initializes the GUI application window and layout."""
        super().__init__()

        self.title("Auto Folder Renamer Pro")
        self.geometry("960x720")
        self.minsize(800, 600)


        self.config_data = RenamerConfig()
        self.dark_mode = False
        self.preview_data: List[Dict[str, str]] = []

        self._init_styles()
        self._build_ui()
        self._load_saved_settings()
        self._apply_theme()

    def _init_styles(self) -> None:
        """Initializes ttk style themes."""
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

    def _apply_theme(self) -> None:
        """Applies light or dark mode theme styling across widgets."""
        if self.dark_mode:
            bg_color = "#1e1e1e"
            fg_color = "#ffffff"
            card_bg = "#2d2d2d"
            accent_color = "#007acc"
            tree_bg = "#252526"
            tree_fg = "#cccccc"
            select_bg = "#37373d"
        else:
            bg_color = "#f4f4f6"
            fg_color = "#111111"
            card_bg = "#ffffff"
            accent_color = "#0066cc"
            tree_bg = "#ffffff"
            tree_fg = "#111111"
            select_bg = "#e5f3ff"

        self.configure(bg=bg_color)
        self.style.configure(".", background=bg_color, foreground=fg_color)
        self.style.configure("Card.TFrame", background=card_bg, relief="flat", borderwidth=1)
        self.style.configure("CardHeader.TLabel", background=card_bg, foreground=fg_color, font=("Segoe UI", 10, "bold"))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), background=bg_color, foreground=fg_color)
        self.style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"))
        self.style.configure("Treeview", background=tree_bg, foreground=tree_fg, fieldbackground=tree_bg, rowheight=24)
        self.style.map("Treeview", background=[("selected", select_bg)], foreground=[("selected", fg_color)])

    def _build_ui(self) -> None:
        """Constructs the complete user interface layout."""
        main_container = ttk.Frame(self, padding=12)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header Title Bar
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(header_frame, text="Auto Folder Renamer Pro", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)

        theme_btn = ttk.Button(header_frame, text="Toggle Dark/Light Mode", command=self._toggle_theme)
        theme_btn.pack(side=tk.RIGHT)

        # Folder Selection Bar
        folder_card = ttk.Frame(main_container, style="Card.TFrame", padding=10)
        folder_card.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(folder_card, text="Target Directory Path:", style="CardHeader.TLabel").pack(anchor=tk.W, pady=(0, 4))
        path_box = ttk.Frame(folder_card)
        path_box.pack(fill=tk.X)

        self.path_entry = ttk.Entry(path_box)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.path_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        browse_btn = ttk.Button(path_box, text="Browse Folder...", command=self._browse_folder)
        browse_btn.pack(side=tk.RIGHT)

        # Presets Bar
        preset_frame = ttk.Frame(main_container)
        preset_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(preset_frame, text="Quick Presets:").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(preset_frame, text="Camera Photos", command=lambda: self._apply_preset("photos")).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="YouTube Projects", command=lambda: self._apply_preset("youtube")).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="School Files", command=lambda: self._apply_preset("school")).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Client Projects", command=lambda: self._apply_preset("client")).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Documents", command=lambda: self._apply_preset("docs")).pack(side=tk.LEFT, padx=2)

        # Options Grid Frame
        options_card = ttk.Frame(main_container, style="Card.TFrame", padding=10)
        options_card.pack(fill=tk.X, pady=(0, 10))

        # Mode Selection
        mode_box = ttk.Frame(options_card)
        mode_box.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(mode_box, text="Rename Mode:", style="CardHeader.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.mode_var = tk.StringVar(value=RenameMode.SEQUENTIAL.value)
        mode_choices = [
            ("Sequential", RenameMode.SEQUENTIAL.value),
            ("Replace Text", RenameMode.REPLACE_TEXT.value),
            ("Add Prefix", RenameMode.ADD_PREFIX.value),
            ("Add Suffix", RenameMode.ADD_SUFFIX.value),
            ("Uppercase", RenameMode.UPPERCASE.value),
            ("Lowercase", RenameMode.LOWERCASE.value),
            ("Title Case", RenameMode.TITLE_CASE.value),
            ("Remove Spaces", RenameMode.REMOVE_SPACES.value),
            ("Replace Spaces (_)", RenameMode.REPLACE_SPACES_UNDERSCORE.value),
            ("Clean Special Chars", RenameMode.REMOVE_SPECIAL_CHARS.value),
        ]

        self.mode_combo = ttk.Combobox(mode_box, values=[m[0] for m in mode_choices], state="readonly", width=22)
        self.mode_combo.current(0)
        self.mode_combo.pack(side=tk.LEFT)
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)

        # Dynamic Controls Frame
        self.dynamic_frame = ttk.Frame(options_card)
        self.dynamic_frame.pack(fill=tk.X, pady=(0, 8))

        # Filter & Sorting Flags Frame
        filter_box = ttk.Frame(options_card)
        filter_box.pack(fill=tk.X)

        self.subfolder_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_box, text="Include Subfolders", variable=self.subfolder_var, command=self.update_preview).pack(side=tk.LEFT, padx=(0, 12))

        self.hidden_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_box, text="Skip Hidden Folders", variable=self.hidden_var, command=self.update_preview).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(filter_box, text="Sort By:").pack(side=tk.LEFT, padx=(8, 4))
        self.sort_combo = ttk.Combobox(filter_box, values=["Alphabetical", "Creation Date", "Modification Date", "Folder Size"], state="readonly", width=16)
        self.sort_combo.current(0)
        self.sort_combo.pack(side=tk.LEFT, padx=(0, 12))
        self.sort_combo.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        ttk.Label(filter_box, text="Duplicate Resolution:").pack(side=tk.LEFT, padx=(8, 4))
        self.dup_combo = ttk.Combobox(filter_box, values=["Skip Collision", "Auto-Index (e.g. Folder (1))"], state="readonly", width=24)
        self.dup_combo.current(0)
        self.dup_combo.pack(side=tk.LEFT)
        self.dup_combo.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        # Live Search Filter & Treeview Preview Table
        preview_header = ttk.Frame(main_container)
        preview_header.pack(fill=tk.X, pady=(4, 4))

        ttk.Label(preview_header, text="Live Preview Table", style="Header.TLabel").pack(side=tk.LEFT)

        search_box = ttk.Frame(preview_header)
        search_box.pack(side=tk.RIGHT)
        ttk.Label(search_box, text="Search Preview:").pack(side=tk.LEFT, padx=(0, 4))
        self.search_entry = ttk.Entry(search_box, width=20)
        self.search_entry.pack(side=tk.LEFT)
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_treeview())

        # Treeview Widget
        tree_frame = ttk.Frame(main_container)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        columns = ("status", "old_name", "new_name", "conflict")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("status", text="Status")
        self.tree.heading("old_name", text="Current Folder Name")
        self.tree.heading("new_name", text="Proposed New Name")
        self.tree.heading("conflict", text="Conflict")

        self.tree.column("status", width=120, anchor=tk.CENTER)
        self.tree.column("old_name", width=340, anchor=tk.W)
        self.tree.column("new_name", width=340, anchor=tk.W)
        self.tree.column("conflict", width=90, anchor=tk.CENTER)

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.tag_configure("conflict", foreground="#d9534f")
        self.tree.tag_configure("ready", foreground="#5cb85c")
        self.tree.tag_configure("unchanged", foreground="#888888")

        # Action Toolbar
        action_bar = ttk.Frame(main_container)
        action_bar.pack(fill=tk.X, pady=(0, 6))

        self.preview_btn = ttk.Button(action_bar, text="Refresh Preview", command=self.update_preview)
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.rename_btn = ttk.Button(action_bar, text="Execute Rename", style="Primary.TButton", command=self._execute_rename)
        self.rename_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.undo_btn = ttk.Button(action_bar, text="Undo Last Session", command=self._execute_undo)
        self.undo_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.export_btn = ttk.Button(action_bar, text="Export CSV History", command=self._export_csv)
        self.export_btn.pack(side=tk.LEFT, padx=(0, 6))

        # Progress Bar & Status Bar
        self.progress_bar = ttk.Progressbar(main_container, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 4))

        self.status_var = tk.StringVar(value="Ready. Select target directory to begin.")
        status_bar = ttk.Label(main_container, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X)

        self._render_dynamic_controls()

    def _render_dynamic_controls(self) -> None:
        """Renders mode-specific inputs in dynamic options frame."""
        for child in self.dynamic_frame.winfo_children():
            child.destroy()

        mode_name = self.mode_combo.get()

        if mode_name == "Sequential":
            ttk.Label(self.dynamic_frame, text="Prefix:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=2)
            self.prefix_entry = ttk.Entry(self.dynamic_frame, width=16)
            self.prefix_entry.insert(0, "Project-")
            self.prefix_entry.grid(row=0, column=1, padx=4, pady=2)
            self.prefix_entry.bind("<KeyRelease>", lambda e: self.update_preview())

            ttk.Label(self.dynamic_frame, text="Start Number:").grid(row=0, column=2, sticky=tk.W, padx=4, pady=2)
            self.start_entry = ttk.Entry(self.dynamic_frame, width=8)
            self.start_entry.insert(0, "1")
            self.start_entry.grid(row=0, column=3, padx=4, pady=2)
            self.start_entry.bind("<KeyRelease>", lambda e: self.update_preview())

            ttk.Label(self.dynamic_frame, text="Min Padding Digits:").grid(row=0, column=4, sticky=tk.W, padx=4, pady=2)
            self.padding_entry = ttk.Entry(self.dynamic_frame, width=6)
            self.padding_entry.insert(0, "3")
            self.padding_entry.grid(row=0, column=5, padx=4, pady=2)
            self.padding_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        elif mode_name == "Replace Text":
            ttk.Label(self.dynamic_frame, text="Find Text:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=2)
            self.find_entry = ttk.Entry(self.dynamic_frame, width=20)
            self.find_entry.grid(row=0, column=1, padx=4, pady=2)
            self.find_entry.bind("<KeyRelease>", lambda e: self.update_preview())

            ttk.Label(self.dynamic_frame, text="Replace With:").grid(row=0, column=2, sticky=tk.W, padx=4, pady=2)
            self.replace_entry = ttk.Entry(self.dynamic_frame, width=20)
            self.replace_entry.grid(row=0, column=3, padx=4, pady=2)
            self.replace_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        elif mode_name in ("Add Prefix", "Add Suffix"):
            ttk.Label(self.dynamic_frame, text="Text String:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=2)
            self.affix_entry = ttk.Entry(self.dynamic_frame, width=24)
            self.affix_entry.grid(row=0, column=1, padx=4, pady=2)
            self.affix_entry.bind("<KeyRelease>", lambda e: self.update_preview())

    def _on_mode_changed(self, event=None) -> None:
        """Handles rename mode combo change."""
        self._render_dynamic_controls()
        self.update_preview()

    def _browse_folder(self) -> None:
        """Opens directory browser dialog."""
        selected = filedialog.askdirectory()
        if selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected)
            self.update_preview()

    def _apply_preset(self, preset_name: str) -> None:
        """Applies predefined naming presets."""
        self.mode_combo.current(0)  # Sequential
        self._render_dynamic_controls()

        if preset_name == "photos":
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.insert(0, "IMG-")
        elif preset_name == "youtube":
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.insert(0, "Video-")
        elif preset_name == "school":
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.insert(0, "Class-")
        elif preset_name == "client":
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.insert(0, "Client-")
        elif preset_name == "docs":
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.insert(0, "Doc-")

        self.update_preview()

    def _get_current_config(self) -> Optional[RenamerConfig]:
        """Constructs RenamerConfig from GUI input values."""
        target_path_str = self.path_entry.get().strip()
        if not target_path_str:
            return None

        target_path = Path(target_path_str)
        mode_map = {
            "Sequential": RenameMode.SEQUENTIAL,
            "Replace Text": RenameMode.REPLACE_TEXT,
            "Add Prefix": RenameMode.ADD_PREFIX,
            "Add Suffix": RenameMode.ADD_SUFFIX,
            "Uppercase": RenameMode.UPPERCASE,
            "Lowercase": RenameMode.LOWERCASE,
            "Title Case": RenameMode.TITLE_CASE,
            "Remove Spaces": RenameMode.REMOVE_SPACES,
            "Replace Spaces (_)": RenameMode.REPLACE_SPACES_UNDERSCORE,
            "Clean Special Chars": RenameMode.REMOVE_SPECIAL_CHARS,
        }

        mode = mode_map.get(self.mode_combo.get(), RenameMode.SEQUENTIAL)

        prefix = "Project-"
        suffix = ""
        find_text = ""
        replace_text = ""
        start = 1
        padding = 3

        if mode == RenameMode.SEQUENTIAL:
            prefix = getattr(self, "prefix_entry", None).get() if hasattr(self, "prefix_entry") else "Project-"
            try:
                start = int(self.start_entry.get().strip())
                padding = int(self.padding_entry.get().strip())
            except ValueError:
                pass
        elif mode == RenameMode.REPLACE_TEXT:
            find_text = getattr(self, "find_entry", None).get() if hasattr(self, "find_entry") else ""
            replace_text = getattr(self, "replace_entry", None).get() if hasattr(self, "replace_entry") else ""
        elif mode == RenameMode.ADD_PREFIX:
            prefix = getattr(self, "affix_entry", None).get() if hasattr(self, "affix_entry") else ""
        elif mode == RenameMode.ADD_SUFFIX:
            suffix = getattr(self, "affix_entry", None).get() if hasattr(self, "affix_entry") else ""

        sort_map = {
            "Alphabetical": SortOrder.ALPHABETICAL,
            "Creation Date": SortOrder.DATE_CREATED,
            "Modification Date": SortOrder.DATE_MODIFIED,
            "Folder Size": SortOrder.FOLDER_SIZE,
        }

        dup_map = {
            "Skip Collision": DuplicateStrategy.SKIP,
            "Auto-Index (e.g. Folder (1))": DuplicateStrategy.AUTO_INDEX,
        }

        return RenamerConfig(
            target_path=target_path,
            mode=mode,
            prefix=prefix,
            suffix=suffix,
            find_text=find_text,
            replace_text=replace_text,
            start=start,
            min_zero_padding=padding,
            include_subfolders=self.subfolder_var.get(),
            skip_hidden=self.hidden_var.get(),
            sort_order=sort_map.get(self.sort_combo.get(), SortOrder.ALPHABETICAL),
            duplicate_strategy=dup_map.get(self.dup_combo.get(), DuplicateStrategy.SKIP),
        )

    def update_preview(self) -> None:
        """Refreshes live preview table based on active controls."""
        config = self._get_current_config()
        if not config or not config.target_path.exists():
            self.preview_data = []
            self._render_treeview(self.preview_data)
            self.status_var.set("Please select a valid directory.")
            return

        try:
            renamer = FolderRenamer(config)
            self.preview_data = renamer.generate_preview()
            self._filter_treeview()

            count = len(self.preview_data)
            conflicts = sum(1 for item in self.preview_data if item.get("conflict") == "Yes")
            self.status_var.set(f"Found {count} folder(s). Conflicts: {conflicts}")
        except Exception as err:
            self.status_var.set(f"Error generating preview: {err}")

    def _filter_treeview(self, event=None) -> None:
        """Filters treeview rows based on search box input."""
        query = self.search_entry.get().strip().lower()
        if not query:
            self._render_treeview(self.preview_data)
            return


        filtered = [
            item for item in self.preview_data
            if query in item["old_name"].lower() or query in item["new_name"].lower()
        ]
        self._render_treeview(filtered)

    def _render_treeview(self, rows: List[Dict[str, str]]) -> None:
        """Populates Treeview widget with row records."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            tag = "ready"
            if row["conflict"] == "Yes":
                tag = "conflict"
            elif row["status"] == "Unchanged":
                tag = "unchanged"

            self.tree.insert(
                "",
                tk.END,
                values=(row["status"], row["old_name"], row["new_name"], row["conflict"]),
                tags=(tag,),
            )

    def _execute_rename(self) -> None:
        """Triggers batch rename operation."""
        config = self._get_current_config()
        if not config:
            messagebox.showwarning("Warning", "Please select a target directory first.")
            return

        renamer = FolderRenamer(config)
        self.progress_bar["value"] = 0

        def progress_cb(current, total):
            pct = (current / total) * 100
            self.progress_bar["value"] = pct
            self.update_idletasks()

        try:
            renamed, skipped = renamer.run(progress_callback=progress_cb)
            self.save_settings()
            messagebox.showinfo("Success", f"Rename complete!\nRenamed: {renamed}\nSkipped: {skipped}")
            self.update_preview()
        except Exception as err:
            messagebox.showerror("Error", f"Rename failed: {err}")

    def _execute_undo(self) -> None:
        """Triggers undo operation restoring original names."""
        config = RenamerConfig(undo=True)
        renamer = FolderRenamer(config)
        try:
            manager = UndoManager(config.history_file)
            latest = manager.get_latest_session()
            if not latest:
                messagebox.showwarning("Warning", "No undo history available to restore.")
                return

            if messagebox.askyesno("Confirm Undo", f"Undo rename session from {latest.get('timestamp')}?"):
                manager.undo_last_session()
                messagebox.showinfo("Success", "Undo completed successfully!")
                self.update_preview()
        except Exception as err:
            messagebox.showerror("Error", f"Undo failed: {err}")

    def _export_csv(self) -> None:
        """Exports history log to CSV file."""
        selected_file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if selected_file:
            manager = UndoManager(RenamerConfig().history_file)
            if manager.export_history_to_csv(Path(selected_file)):
                messagebox.showinfo("Success", f"History exported successfully to {selected_file}")
            else:
                messagebox.showwarning("Warning", "No history available to export.")

    def _toggle_theme(self) -> None:
        """Toggles between dark and light mode themes."""
        self.dark_mode = not self.dark_mode
        self._apply_theme()

    def _load_saved_settings(self) -> None:
        """Loads last-used GUI settings from JSON config file."""
        settings_file = Path.home() / ".folder_auto_renamer_gui_settings.json"
        if not settings_file.exists():
            return
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "target_path" in data and os.path.exists(data["target_path"]):
                    self.path_entry.insert(0, data["target_path"])
                if "dark_mode" in data:
                    self.dark_mode = bool(data["dark_mode"])
        except Exception:
            pass

    def save_settings(self) -> None:
        """Saves current GUI settings to JSON config file."""
        settings_file = Path.home() / ".folder_auto_renamer_gui_settings.json"
        try:
            data = {
                "target_path": self.path_entry.get().strip(),
                "dark_mode": self.dark_mode,
            }
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass


def launch_gui() -> None:
    """Launches the Tkinter GUI mainloop."""
    app = RenamerGUI()
    app.deiconify()
    app.lift()
    app.focus_force()
    app.mainloop()



if __name__ == "__main__":
    launch_gui()
