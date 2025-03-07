import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import threading
from datetime import datetime

class DestinationPopup:
    def __init__(self, parent, callback):
        self.top = tk.Toplevel(parent)
        self.top.title("Select Backup Destination")
        self.top.geometry("500x200")
        self.top.transient(parent)
        self.top.grab_set()
        self.callback = callback

        main_frame = ttk.Frame(self.top, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Backup Destination:").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.destination_path = tk.StringVar()
        self.destination_entry = ttk.Entry(main_frame, textvariable=self.destination_path, width=50)
        self.destination_entry.grid(row=1, column=0, padx=(0, 5), sticky="ew")
        ttk.Button(main_frame, text="Browse", command=self.browse_destination).grid(row=1, column=1)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="OK", command=self.on_ok).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.top.destroy).grid(row=0, column=1, padx=5)

        main_frame.columnconfigure(0, weight=1)

    def browse_destination(self):
        directory = filedialog.askdirectory(initialdir="/")
        if directory:
            self.destination_path.set(directory)

    def on_ok(self):
        if self.destination_path.get():
            self.callback(self.destination_path.get())
            self.top.destroy()
        else:
            messagebox.showwarning("Warning", "Please select a destination directory")

class CustomFoldersPopup:
    def __init__(self, parent, callback):
        self.top = tk.Toplevel(parent)
        self.top.title("Select Folders to Backup")
        self.top.geometry("500x300")
        self.top.transient(parent)
        self.top.grab_set()
        self.callback = callback
        self.folders = []

        main_frame = ttk.Frame(self.top, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Selected Folders:").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self.folder_listbox = tk.Listbox(main_frame, height=10, width=50)
        self.folder_listbox.grid(row=1, column=0, columnspan=2, sticky="nsew")

        ttk.Button(main_frame, text="Add Folder", command=self.add_folder).grid(row=2, column=0, pady=10)
        ttk.Button(main_frame, text="Remove Selected", command=self.remove_folder).grid(row=2, column=1, pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="OK", command=self.on_ok).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.top.destroy).grid(row=0, column=1, padx=5)

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

    def add_folder(self):
        folder = filedialog.askdirectory(initialdir="/")
        if folder and folder not in self.folders:
            self.folders.append(folder)
            self.folder_listbox.insert(tk.END, folder)

    def remove_folder(self):
        selection = self.folder_listbox.curselection()
        if selection:
            index = selection[0]
            self.folder_listbox.delete(index)
            self.folders.pop(index)

    def on_ok(self):
        if self.folders:
            self.callback(self.folders)
            self.top.destroy()
        else:
            messagebox.showwarning("Warning", "Please select at least one folder to backup")

class UserProfileBackupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("User Profile Backup Utility")
        self.root.geometry("600x700")
        self.root.resizable(True, True)

        self.user_profile = os.path.expanduser("~")
        self.default_destination = "D:\\UserProfileBackups"

        self.source_paths = {
            "documents": os.path.join(self.user_profile, "Documents"),
            "desktop": os.path.join(self.user_profile, "Desktop"),
            "pictures": os.path.join(self.user_profile, "Pictures"),
            "all": self.user_profile,
            "custom": []
        }

        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", padding=6, relief="flat", background="#0078d7")
        self.style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))

        self.main_frame = ttk.Frame(self.root, padding="20", style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.main_frame, text="User Profile Backup System", style="Header.TLabel").grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")

        ttk.Label(self.main_frame, text="Select Backup Type:").grid(row=1, column=0, sticky="w", pady=(10, 5))
        self.backup_type = tk.StringVar(value="documents")
        ttk.Radiobutton(self.main_frame, text="Documents Only", variable=self.backup_type, value="documents").grid(row=2, column=0, sticky="w", padx=(20, 0))
        ttk.Radiobutton(self.main_frame, text="Desktop Only", variable=self.backup_type, value="desktop").grid(row=3, column=0, sticky="w", padx=(20, 0))
        ttk.Radiobutton(self.main_frame, text="Pictures Only", variable=self.backup_type, value="pictures").grid(row=4, column=0, sticky="w", padx=(20, 0))
        ttk.Radiobutton(self.main_frame, text="Full Profile (Documents, Desktop, Pictures, etc.)", variable=self.backup_type, value="all").grid(row=5, column=0, sticky="w", padx=(20, 0))
        ttk.Radiobutton(self.main_frame, text="Custom Folders (Select specific folders)", variable=self.backup_type, value="custom", command=self.show_custom_folders_popup).grid(row=6, column=0, sticky="w", padx=(20, 0))

        ttk.Label(self.main_frame, text="Backup Speed:").grid(row=7, column=0, sticky="w", pady=(20, 5))
        self.slow_backup = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.main_frame, text="Slow Backup (Single-threaded for defective drives)",
                       variable=self.slow_backup).grid(row=8, column=0, sticky="w", padx=(20, 0))

        ttk.Label(self.main_frame, text="Selected Destination:").grid(row=9, column=0, sticky="w", pady=(20, 5))
        self.destination_var = tk.StringVar(value="Not selected yet")
        self.destination_label = ttk.Label(self.main_frame, textvariable=self.destination_var, wraplength=550)
        self.destination_label.grid(row=10, column=0, columnspan=3, sticky="w", padx=(20, 0))

        ttk.Label(self.main_frame, text="Backup Folder Structure:").grid(row=11, column=0, sticky="w", pady=(10, 5))
        self.folder_preview_var = tk.StringVar(value="Select a destination to see folder structure")
        self.folder_preview_label = ttk.Label(self.main_frame, textvariable=self.folder_preview_var, wraplength=550)
        self.folder_preview_label.grid(row=12, column=0, columnspan=3, sticky="w", padx=(20, 0))

        ttk.Label(self.main_frame, text="Status:").grid(row=13, column=0, sticky="w", pady=(20, 5))
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.main_frame, textvariable=self.status_var).grid(row=14, column=0, columnspan=3, sticky="w", padx=(20, 0))

        self.progress = ttk.Progressbar(self.main_frame, orient="horizontal", length=550, mode="indeterminate")
        self.progress.grid(row=15, column=0, columnspan=3, pady=(10, 20), sticky="ew")

        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=16, column=0, columnspan=3, pady=10, sticky="e")
        self.select_dest_button = ttk.Button(button_frame, text="Select Destination", command=self.show_destination_popup)
        self.select_dest_button.grid(row=0, column=0, padx=(0, 10))
        self.backup_button = ttk.Button(button_frame, text="Start Backup", command=self.start_backup, state="disabled")
        self.backup_button.grid(row=0, column=1, padx=(0, 10))
        self.exit_button = ttk.Button(button_frame, text="Exit", command=self.root.destroy)
        self.exit_button.grid(row=0, column=2)

        self.backup_type.trace_add("write", lambda *args: self.update_folder_preview())

    def show_destination_popup(self):
        DestinationPopup(self.root, self.set_destination)

    def show_custom_folders_popup(self):
        if self.backup_type.get() == "custom":
            CustomFoldersPopup(self.root, self.set_custom_folders)

    def set_custom_folders(self, folders):
        self.source_paths["custom"] = folders
        self.update_folder_preview()

    def set_destination(self, destination):
        self.destination_var.set(destination)
        self.destination = os.path.normpath(destination)
        self.update_folder_preview()
        self.backup_button.configure(state="normal")

    def update_folder_preview(self):
        if self.destination_var.get() == "Not selected yet":
            self.folder_preview_var.set("Select a destination to see folder structure")
            return

        base_destination = self.destination_var.get()
        backup_type = self.backup_type.get()

        if backup_type == "custom" and not self.source_paths["custom"]:
            preview = "Select folders to see structure"
        elif backup_type == "custom":
            preview = "\n".join(f"{base_destination}\\{os.path.splitdrive(source)[0].rstrip(':')}{os.path.splitdrive(source)[1]}\\..." for source in self.source_paths["custom"])
        else:
            source = self.source_paths[backup_type]
            preview = f"{base_destination}\\{os.path.splitdrive(source)[0].rstrip(':')}{os.path.splitdrive(source)[1]}\\..."

        self.folder_preview_var.set(preview)

    def start_backup(self):
        if not hasattr(self, 'destination') or not self.destination:
            messagebox.showwarning("Warning", "Please select a destination first")
            return
        if self.backup_type.get() == "custom" and not self.source_paths["custom"]:
            messagebox.showwarning("Warning", "Please select at least one folder for custom backup")
            return

        self.backup_button.configure(state="disabled")
        self.select_dest_button.configure(state="disabled")
        self.progress.start()
        backup_thread = threading.Thread(target=self.perform_backup)
        backup_thread.daemon = True
        backup_thread.start()

    def perform_backup(self):
        base_destination = self.destination
        log_file = os.path.join(base_destination, 'backup_log.txt')
        try:
            backup_type = self.backup_type.get()
            backup_root = base_destination  # No timestamp in folder name

            # Log the start of the backup
            with open(log_file, 'a') as f:
                f.write(f"Backup started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            if backup_type == "custom":
                sources = self.source_paths["custom"]
            else:
                sources = [self.source_paths[backup_type]]

            folders_to_backup = []
            for source in sources:
                if not os.path.exists(source):
                    raise FileNotFoundError(f"Source path does not exist: {source}")

                drive, path = os.path.splitdrive(source)  # e.g., "C:", "\AIO"
                if not drive:
                    raise ValueError(f"Invalid source path (no drive letter): {source}")

                # Preserve drive as folder and full path (e.g., "C\AIO")
                relative_path = os.path.join(drive.rstrip(':'), path.lstrip(os.sep))
                destination = os.path.normpath(os.path.join(backup_root, relative_path))

                print(f"Source: {source}")
                print(f"Destination: {destination}")

                source_contents = os.listdir(source) if os.path.isdir(source) else []
                print(f"Source contents: {source_contents}")

                if not source_contents:
                    self.status_var.set(f"Skipped backup of {os.path.basename(source)} (source is empty)")
                    with open(log_file, 'a') as f:
                        f.write(f"Source: {source}\n")
                        f.write(f"Destination: {destination}\n")
                        f.write(f"Status: Skipped (source is empty)\n")
                    continue

                if os.path.exists(destination):
                    response = messagebox.askyesno(
                        "Folder Exists",
                        f"The folder '{destination}' already exists.\n\nDo you want to overwrite it? (Yes = Overwrite, No = Skip)",
                        icon="warning"
                    )
                    if not response:
                        self.status_var.set(f"Skipped backup of {os.path.basename(source)} (folder exists)")
                        with open(log_file, 'a') as f:
                            f.write(f"Source: {source}\n")
                            f.write(f"Destination: {destination}\n")
                            f.write(f"Status: Skipped (folder exists)\n")
                        continue

                folders_to_backup.append((source, destination))

            if not folders_to_backup:
                self.status_var.set("No folders backed up (all skipped or empty)")
                with open(log_file, 'a') as f:
                    f.write("No folders backed up (all skipped or empty)\n")
                messagebox.showinfo("Backup Complete", f"No folders were backed up as all were skipped or empty. Details are logged in {log_file}.")
                return

            for source, destination in folders_to_backup:
                self.status_var.set(f"Backing up {os.path.basename(source)}...")
                self.root.update_idletasks()

                os.makedirs(os.path.dirname(destination), exist_ok=True)

                robocopy_cmd = [
                    "robocopy",
                    source,
                    destination,
                    "/E",
                    "/R:5",
                    "/W:5",
                    "/V",
                ]
                if backup_type == "all":
                    robocopy_cmd.extend(["/XD", "AppData"])
                if not self.slow_backup.get():
                    robocopy_cmd.append("/MT:8")

                print("Executing command:", " ".join(robocopy_cmd))
                result = subprocess.run(robocopy_cmd, capture_output=True, text=True)

                print(f"Robocopy stdout: {result.stdout}")
                print(f"Robocopy stderr: {result.stderr}")
                print(f"Return code: {result.returncode}")

                if result.returncode > 1:
                    raise subprocess.CalledProcessError(result.returncode, robocopy_cmd, output=result.stdout, stderr=result.stderr)
                elif result.returncode == 1:
                    self.status_var.set(f"Backup of {os.path.basename(source)} completed with files copied")
                    with open(log_file, 'a') as f:
                        f.write(f"Source: {source}\n")
                        f.write(f"Destination: {destination}\n")
                        f.write(f"Status: Completed with files copied\n")
                elif result.returncode == 0:
                    self.status_var.set(f"Backup of {os.path.basename(source)} completed (no new/changed files to copy)")
                    with open(log_file, 'a') as f:
                        f.write(f"Source: {source}\n")
                        f.write(f"Destination: {destination}\n")
                        f.write(f"Status: Completed (no new/changed files to copy)\n")
                else:
                    self.status_var.set(f"Backup of {os.path.basename(source)} completed with status {result.returncode}")
                    with open(log_file, 'a') as f:
                        f.write(f"Source: {source}\n")
                        f.write(f"Destination: {destination}\n")
                        f.write(f"Status: Completed with status {result.returncode}\n")

            # Log the completion of the backup
            with open(log_file, 'a') as f:
                f.write(f"Backup completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            self.status_var.set(f"Backup completed successfully to {backup_root}")
            messagebox.showinfo("Backup Complete", f"The {backup_type} backup has been completed successfully. Details are logged in {log_file}.")

        except subprocess.CalledProcessError as e:
            error_msg = f"Robocopy failed with exit code {e.returncode}: {e.stderr or e.output}"
            self.status_var.set(f"Error: {error_msg}")
            with open(log_file, 'a') as f:
                f.write(f"Error: {error_msg}\n")
            messagebox.showerror("Backup Failed", error_msg)
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            with open(log_file, 'a') as f:
                f.write(f"Error: {str(e)}\n")
            messagebox.showerror("Backup Failed", f"An error occurred during backup: {str(e)}")
        finally:
            self.progress.stop()
            self.backup_button.configure(state="normal")
            self.select_dest_button.configure(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = UserProfileBackupGUI(root)
    root.mainloop()
