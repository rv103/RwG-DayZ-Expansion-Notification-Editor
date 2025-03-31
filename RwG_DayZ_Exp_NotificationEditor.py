import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class NotificationEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("RwG DayZ Expansion Notification Editor")
        self.data = {}
        self.current_file = None
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("vista")  # Alternativen: 'vista', 'alt', 'default'

        # Top Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Open File", command=self.load_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save", command=self.save_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save As...", command=self.save_file_as).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Add Notification", command=self.add_notification).pack(side="right", padx=5)

        # General Settings
        self.general_frame = ttk.LabelFrame(frame, text="General Settings")
        self.general_frame.pack(fill="x", pady=5)

        self.enabled_var = tk.IntVar()
        self.utc_var = tk.IntVar()
        self.use_mission_var = tk.IntVar()
        self.version_var = tk.IntVar()

        ttk.Checkbutton(self.general_frame, text="Enable Notifications", variable=self.enabled_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(self.general_frame, text="Use UTC", variable=self.utc_var).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(self.general_frame, text="Use Mission Time", variable=self.use_mission_var).grid(row=0, column=2, sticky="w")
        ttk.Label(self.general_frame, text="Version:").grid(row=1, column=0, sticky="e")
        ttk.Entry(self.general_frame, textvariable=self.version_var, width=5).grid(row=1, column=1, sticky="w")

        # Notification List
        self.notif_frame = ttk.LabelFrame(frame, text="Notifications")
        self.notif_frame.pack(fill="both", expand=True, pady=5)

        self.tree = ttk.Treeview(self.notif_frame, columns=("Hour", "Minute", "Second", "Title", "Text", "Icon", "Color"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)

        ttk.Button(self.notif_frame, text="Delete Selected Notification", command=self.delete_notification).pack(pady=5)

        self.tree.bind("<Double-1>", self.edit_notification)

    def update_title(self):
        if self.current_file:
            self.root.title(f"RwG DayZ Expansion Notification Editor - {self.current_file}")
        else:
            self.root.title("RwG DayZ Expansion Notification Editor")

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        with open(path, "r") as f:
            self.data = json.load(f)
        self.current_file = path
        self.update_title()
        self.refresh_ui()

    def refresh_ui(self):
        self.version_var.set(self.data.get("m_Version", 1))
        self.enabled_var.set(self.data.get("Enabled", 0))
        self.utc_var.set(self.data.get("UTC", 0))
        self.use_mission_var.set(self.data.get("UseMissionTime", 0))

        for row in self.tree.get_children():
            self.tree.delete(row)
        for n in self.data.get("Notifications", []):
            self.tree.insert("", "end", values=(
                n.get("Hour", 0),
                n.get("Minute", 0),
                n.get("Second", 0),
                n.get("Title", ""),
                n.get("Text", ""),
                n.get("Icon", ""),
                n.get("Color", "")
            ))

    def save_file(self):
        if not self.current_file:
            self.save_file_as()
            return
        self.data["m_Version"] = self.version_var.get()
        self.data["Enabled"] = self.enabled_var.get()
        self.data["UTC"] = self.utc_var.get()
        self.data["UseMissionTime"] = self.use_mission_var.get()
        with open(self.current_file, "w") as f:
            json.dump(self.data, f, indent=4)
        messagebox.showinfo("Success", f"File saved: {self.current_file}")

    def save_file_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        self.current_file = path
        self.update_title()
        self.save_file()

    def edit_notification(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        self.open_editor(index)

    def add_notification(self):
        self.data.setdefault("Notifications", []).append({
            "Hour": 0, "Minute": 0, "Second": 0,
            "Title": "", "Text": "",
            "Icon": "", "Color": ""
        })
        self.refresh_ui()

    def delete_notification(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select an entry to delete.")
            return
        index = self.tree.index(selected[0])
        confirm = messagebox.askyesno("Confirm deletion", "Are you sure you want to delete this notification?")
        if confirm:
            del self.data["Notifications"][index]
            self.refresh_ui()

    def open_editor(self, index):
        notif = self.data["Notifications"][index]
        editor = tk.Toplevel(self.root)
        editor.title("Edit Notification")

        def validate_int_limited(entry_type):
            def validator(new_value):
                if not new_value.isdigit():
                    return False
                value = int(new_value)
                if entry_type == "hour":
                    return 0 <= value <= 23
                elif entry_type in ["minute", "second"]:
                    return 0 <= value <= 59
                return False
            return validator

        vcmd_hour = (editor.register(validate_int_limited("hour")), "%P")
        vcmd_min = (editor.register(validate_int_limited("minute")), "%P")
        vcmd_sec = (editor.register(validate_int_limited("second")), "%P")

        hour_var = tk.StringVar(value=notif["Hour"])
        minute_var = tk.StringVar(value=notif["Minute"])
        second_var = tk.StringVar(value=notif["Second"])
        title_var = tk.StringVar(value=notif["Title"])
        text_var = tk.StringVar(value=notif["Text"])
        icon_var = tk.StringVar(value=notif["Icon"])
        color_var = tk.StringVar(value=notif["Color"])

        entries = [
            ("Hour", hour_var),
            ("Minute", minute_var),
            ("Second", second_var),
            ("Title", title_var),
            ("Text", text_var),
            ("Icon", icon_var),
            ("Color", color_var)
        ]

        for i, (label, var) in enumerate(entries):
            ttk.Label(editor, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)

            if label == "Text":
                text_widget = tk.Text(editor, height=4, width=70, wrap="word")
                text_widget.insert("1.0", var.get())
                text_widget.grid(row=i, column=1, sticky="w", padx=5, pady=2)
                entries[i] = (label, text_widget)
            elif label == "Hour":
                ttk.Entry(editor, textvariable=var, width=5, validate="key", validatecommand=vcmd_hour).grid(row=i, column=1, sticky="w", padx=5, pady=2)
            elif label == "Minute":
                ttk.Entry(editor, textvariable=var, width=5, validate="key", validatecommand=vcmd_min).grid(row=i, column=1, sticky="w", padx=5, pady=2)
            elif label == "Second":
                ttk.Entry(editor, textvariable=var, width=5, validate="key", validatecommand=vcmd_sec).grid(row=i, column=1, sticky="w", padx=5, pady=2)
            else:
                entry_width = 70 if label == "Title" else 40
                ttk.Entry(editor, textvariable=var, width=entry_width).grid(row=i, column=1, sticky="w", padx=5, pady=2)

        def save_changes():
            notif["Hour"] = int(hour_var.get())
            notif["Minute"] = int(minute_var.get())
            notif["Second"] = int(second_var.get())
            notif["Title"] = title_var.get()
            for label, widget in entries:
                if label == "Text":
                    notif["Text"] = widget.get("1.0", "end").strip()
            notif["Icon"] = icon_var.get()
            notif["Color"] = color_var.get()
            self.refresh_ui()
            editor.destroy()

        ttk.Button(editor, text="Save", command=save_changes).grid(row=len(entries), column=0, columnspan=2, pady=10)

# Start App
if __name__ == "__main__":
    root = tk.Tk()
    app = NotificationEditor(root)
    root.mainloop()
