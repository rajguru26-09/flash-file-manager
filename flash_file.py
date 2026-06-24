import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path

# ========== CYBERPUNK THEME COLORS ==========
COLOR_BG = "#0a0a12"
COLOR_PANEL = "#1e293b"
COLOR_ACCENT = "#06b6d4"
COLOR_SUCCESS = "#10b981"
COLOR_ERROR = "#ef4444"
COLOR_TEXT = "#e2e8f0"
COLOR_TEXT_DIM = "#94a3b8"

class FlashFileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Flash File Manager 3.0 Pro")
        self.root.geometry("1200x750")
        self.root.configure(bg=COLOR_BG)
        
        # ========== STATE MANAGEMENT ==========
        self.target_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.auto_agent_active = False
        self.agent_thread = None
        self.stop_event = threading.Event()
        self.separate_subtypes = tk.BooleanVar(value=False)  # NEW: Subtype separation toggle
        
        # ========== COMPREHENSIVE FILE TYPE DATABASE ==========
        self.file_categories = {
            "Images": {
                "Photos": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
                "Raw_Images": [".raw", ".cr2", ".nef", ".arw"],
                "Vector_Graphics": [".svg", ".ai", ".eps"],
                "Web_Images": [".webp", ".ico", ".tiff"]
            },
            "Documents": {
                "Word_Files": [".doc", ".docx", ".odt"],
                "Excel_Files": [".xls", ".xlsx", ".csv", ".ods"],
                "PowerPoint_Files": [".ppt", ".pptx", ".odp"],
                "PDF_Files": [".pdf"],
                "Text_Files": [".txt", ".rtf", ".log"],
                "eBooks": [".epub", ".mobi", ".azw"]
            },
            "Videos": {
                "HD_Videos": [".mp4", ".mkv", ".mov"],
                "Web_Videos": [".webm", ".flv"],
                "Legacy_Videos": [".avi", ".wmv", ".mpg", ".mpeg"]
            },
            "Audio": {
                "Music": [".mp3", ".m4a", ".aac"],
                "Lossless": [".flac", ".wav", ".alac"],
                "Other_Audio": [".ogg", ".wma", ".opus"]
            },
            "Archives": {
                "ZIP_Archives": [".zip"],
                "RAR_Archives": [".rar"],
                "Other_Compressed": [".7z", ".tar", ".gz", ".bz2", ".xz"]
            },
            "Software": {
                "Windows_Apps": [".exe", ".msi"],
                "Installers": [".dmg", ".pkg", ".deb", ".rpm"],
                "Mobile_Apps": [".apk", ".ipa"],
                "Scripts": [".bat", ".sh", ".ps1"]
            },
            "Code": {
                "Python_Files": [".py", ".ipynb"],
                "Web_Files": [".html", ".css", ".js", ".jsx", ".ts", ".tsx"],
                "Java_Files": [".java", ".class", ".jar"],
                "C_CPP_Files": [".c", ".cpp", ".h", ".hpp"],
                "Data_Files": [".json", ".xml", ".yaml", ".yml", ".sql"]
            },
            "Design": {
                "Photoshop": [".psd", ".psb"],
                "3D_Models": [".blend", ".obj", ".fbx", ".stl"],
                "CAD_Files": [".dwg", ".dxf"],
                "Fonts": [".ttf", ".otf", ".woff", ".woff2"]
            }
        }
        
        # Flatten for quick lookup: extension -> (category, subcategory)
        self.ext_map = {}
        for category, subtypes in self.file_categories.items():
            for subtype, extensions in subtypes.items():
                for ext in extensions:
                    self.ext_map[ext.lower()] = (category, subtype)
        
        # ========== GUI SETUP ==========
        self.setup_gui()
        self.log_message("✨ Flash File Manager initialized", "INFO")
        self.log_message(f"📂 Monitoring: {self.target_dir}", "INFO")
    
    def setup_gui(self):
        # ========== TOP HEADER ==========
        header = tk.Frame(self.root, bg=COLOR_PANEL, height=80)
        header.pack(fill="x", padx=10, pady=(10, 0))
        header.pack_propagate(False)
        
        tk.Label(header, text="⚡ FLASH FILE MANAGER", font=("Consolas", 24, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_ACCENT).pack(pady=10)
        tk.Label(header, text="AUTONOMOUS FILE ORGANIZATION SYSTEM", font=("Consolas", 10),
                 bg=COLOR_PANEL, fg=COLOR_TEXT_DIM).pack()
        
        # ========== CONTROL PANEL ==========
        control_frame = tk.Frame(self.root, bg=COLOR_BG)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Left Section: Path Selection
        path_frame = tk.Frame(control_frame, bg=COLOR_PANEL, relief="flat", bd=2)
        path_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        tk.Label(path_frame, text="🎯 Target Directory", font=("Consolas", 11, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_ACCENT).pack(anchor="w", padx=10, pady=(10, 5))
        
        path_inner = tk.Frame(path_frame, bg=COLOR_PANEL)
        path_inner.pack(fill="x", padx=10, pady=(0, 10))
        
        self.path_entry = tk.Entry(path_inner, font=("Consolas", 10), bg="#334155",
                                    fg=COLOR_TEXT, insertbackground=COLOR_ACCENT, bd=0, relief="flat")
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 5))
        self.path_entry.insert(0, self.target_dir)
        
        browse_btn = tk.Button(path_inner, text="📁 BROWSE", font=("Consolas", 9, "bold"),
                                bg="#475569", fg=COLOR_TEXT, activebackground="#64748b",
                                bd=0, padx=15, command=self.browse_directory)
        browse_btn.pack(side="right")
        
        # Right Section: Sub-folder Toggle
        toggle_frame = tk.Frame(control_frame, bg=COLOR_PANEL, relief="flat", bd=2)
        toggle_frame.pack(side="right", padx=(5, 0))
        
        tk.Label(toggle_frame, text="⚙️ ADVANCED OPTIONS", font=("Consolas", 11, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_ACCENT).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.subtype_check = tk.Checkbutton(
            toggle_frame, 
            text="📂 Separate into Sub-folders\n(e.g., Documents/Word_Files, Documents/PDF_Files)",
            variable=self.separate_subtypes,
            font=("Consolas", 9),
            bg=COLOR_PANEL, fg=COLOR_TEXT, selectcolor="#334155",
            activebackground=COLOR_PANEL, activeforeground=COLOR_ACCENT,
            bd=0, highlightthickness=0
        )
        self.subtype_check.pack(anchor="w", padx=10, pady=(0, 10))
        
        # ========== ACTION BUTTONS ==========
        button_frame = tk.Frame(self.root, bg=COLOR_BG)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        self.clean_btn = tk.Button(button_frame, text="⚡ CLEAN NOW", font=("Consolas", 12, "bold"),
                                    bg=COLOR_SUCCESS, fg="black", activebackground="#059669",
                                    bd=0, relief="flat", padx=20, pady=12, command=self.clean_now)
        self.clean_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        self.auto_btn = tk.Button(button_frame, text="🤖 START AUTO-AGENT", font=("Consolas", 12, "bold"),
                                   bg="#4f46e5", fg=COLOR_TEXT, activebackground="#4338ca",
                                   bd=0, relief="flat", padx=20, pady=12, command=self.toggle_auto_agent)
        self.auto_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        self.stats_btn = tk.Button(button_frame, text="📊 STATISTICS", font=("Consolas", 12, "bold"),
                                    bg="#334155", fg=COLOR_TEXT, activebackground="#475569",
                                    bd=0, relief="flat", padx=20, pady=12, command=self.show_statistics)
        self.stats_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        # ========== STATUS BAR ==========
        status_frame = tk.Frame(self.root, bg=COLOR_PANEL, height=40)
        status_frame.pack(fill="x", padx=10, pady=(5, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="⏸ IDLE", font=("Consolas", 10, "bold"),
                                      bg=COLOR_PANEL, fg=COLOR_TEXT_DIM, anchor="w")
        self.status_label.pack(side="left", padx=15, fill="y")
        
        self.time_label = tk.Label(status_frame, text="", font=("Consolas", 10),
                                    bg=COLOR_PANEL, fg=COLOR_TEXT_DIM, anchor="e")
        self.time_label.pack(side="right", padx=15, fill="y")
        self.update_time()
        
        # ========== LOG CONSOLE ==========
        log_frame = tk.Frame(self.root, bg=COLOR_BG)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        log_header = tk.Frame(log_frame, bg=COLOR_PANEL, height=35)
        log_header.pack(fill="x")
        log_header.pack_propagate(False)
        
        tk.Label(log_header, text="📜 SYSTEM LOG CONSOLE", font=("Consolas", 11, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_ACCENT).pack(side="left", padx=15, pady=8)
        
        clear_btn = tk.Button(log_header, text="🗑 CLEAR", font=("Consolas", 9, "bold"),
                              bg="#475569", fg=COLOR_TEXT, activebackground="#64748b",
                              bd=0, padx=10, command=self.clear_log)
        clear_btn.pack(side="right", padx=10)
        
        self.log_console = scrolledtext.ScrolledText(
            log_frame, font=("Consolas", 10), bg="#0f172a", fg=COLOR_TEXT,
            insertbackground=COLOR_ACCENT, bd=0, relief="flat", wrap="word", state="disabled"
        )
        self.log_console.pack(fill="both", expand=True)
        
        # Log styling
        self.log_console.tag_config("INFO", foreground="#3b82f6")
        self.log_console.tag_config("SUCCESS", foreground=COLOR_SUCCESS)
        self.log_console.tag_config("ERROR", foreground=COLOR_ERROR)
        self.log_console.tag_config("WARNING", foreground="#f59e0b")
    
    # ========== THREADING LOGIC FOR AUTO-AGENT ==========
    def toggle_auto_agent(self):
        """
        VIVA EXPLANATION:
        This method manages the background automation agent using threading.
        When activated, it spawns a daemon thread that continuously monitors
        the directory every 5 minutes (300 seconds) without blocking the GUI.
        """
        if not self.auto_agent_active:
            # START AUTO-AGENT
            self.auto_agent_active = True
            self.stop_event.clear()  # Reset stop signal
            
            # Create daemon thread for background operation
            self.agent_thread = threading.Thread(target=self.auto_agent_loop, daemon=True)
            self.agent_thread.start()
            
            self.auto_btn.config(text="⏹ STOP AUTO-AGENT", bg=COLOR_ERROR)
            self.status_label.config(text="🤖 AUTO-AGENT ACTIVE", fg=COLOR_SUCCESS)
            self.log_message("🤖 Auto-Agent activated - Monitoring every 5 minutes", "SUCCESS")
        else:
            # STOP AUTO-AGENT
            self.stop_event.set()  # Signal thread to stop
            self.auto_agent_active = False
            
            self.auto_btn.config(text="🤖 START AUTO-AGENT", bg="#4f46e5")
            self.status_label.config(text="⏸ IDLE", fg=COLOR_TEXT_DIM)
            self.log_message("⏹ Auto-Agent deactivated", "WARNING")
    
    def auto_agent_loop(self):
        """
        VIVA EXPLANATION:
        This is the background worker function running in a separate thread.
        It uses threading.Event().wait() for interruptible sleep, allowing
        immediate response to stop signals while maintaining 5-minute intervals.
        The loop exits cleanly when stop_event is set.
        """
        while not self.stop_event.is_set():
            try:
                self.log_message("🔄 Auto-Agent scan initiated...", "INFO")
                self.organize_files()
                self.log_message(f"⏳ Next scan in 5 minutes...", "INFO")
                
                # Interruptible sleep (responds to stop_event immediately)
                if self.stop_event.wait(timeout=300):  # 300 seconds = 5 minutes
                    break  # Stop signal received
                    
            except Exception as e:
                self.log_message(f"❌ Auto-Agent error: {str(e)}", "ERROR")
                self.stop_event.wait(timeout=60)  # Retry after 1 minute on error
    
    # ========== CORE FILE ORGANIZATION LOGIC ==========
    def organize_files(self):
        """Main file organization engine with deep folder nesting support"""
        target_path = Path(self.path_entry.get())
        
        if not target_path.exists():
            self.log_message(f"❌ Directory not found: {target_path}", "ERROR")
            messagebox.showerror("Error", "Target directory does not exist!")
            return
        
        moved_count = 0
        error_count = 0
        use_subtypes = self.separate_subtypes.get()
        
        try:
            # Scan all files in target directory (non-recursive to avoid moving organized files)
            files = [f for f in target_path.iterdir() if f.is_file()]
            
            if not files:
                self.log_message("ℹ️ No files to organize", "INFO")
                return
            
            for file_path in files:
                try:
                    ext = file_path.suffix.lower()
                    
                    if ext in self.ext_map:
                        category, subtype = self.ext_map[ext]
                        
                        # Determine destination based on user preference
                        if use_subtypes:
                            # Deep nesting: Category/Subtype/file.ext
                            dest_folder = target_path / category / subtype
                        else:
                            # Flat structure: Category/file.ext
                            dest_folder = target_path / category
                        
                        # Create folder structure if it doesn't exist
                        dest_folder.mkdir(parents=True, exist_ok=True)
                        
                        # Move file
                        dest_path = dest_folder / file_path.name
                        
                        # Handle duplicate filenames
                        if dest_path.exists():
                            stem = file_path.stem
                            suffix = file_path.suffix
                            counter = 1
                            while dest_path.exists():
                                dest_path = dest_folder / f"{stem}_{counter}{suffix}"
                                counter += 1
                        
                        shutil.move(str(file_path), str(dest_path))
                        
                        # Log with full path structure
                        relative_dest = dest_path.relative_to(target_path)
                        self.log_message(f"✅ Moved: {file_path.name} → {relative_dest}", "SUCCESS")
                        moved_count += 1
                        
                    else:
                        # Unknown file types go to "Others" folder
                        others_folder = target_path / "Others"
                        others_folder.mkdir(exist_ok=True)
                        
                        dest_path = others_folder / file_path.name
                        if dest_path.exists():
                            stem = file_path.stem
                            suffix = file_path.suffix
                            counter = 1
                            while dest_path.exists():
                                dest_path = others_folder / f"{stem}_{counter}{suffix}"
                                counter += 1
                        
                        shutil.move(str(file_path), str(dest_path))
                        self.log_message(f"⚠️ Unknown type: {file_path.name} → Others/", "WARNING")
                        moved_count += 1
                        
                except PermissionError:
                    self.log_message(f"🔒 Permission denied: {file_path.name}", "ERROR")
                    error_count += 1
                except Exception as e:
                    self.log_message(f"❌ Error moving {file_path.name}: {str(e)}", "ERROR")
                    error_count += 1
            
            # Summary
            self.log_message(f"✨ Organization complete: {moved_count} files moved, {error_count} errors", "SUCCESS")
            
        except Exception as e:
            self.log_message(f"❌ Critical error: {str(e)}", "ERROR")
    
    def clean_now(self):
        """Manual trigger for file organization"""
        self.status_label.config(text="⚡ PROCESSING...", fg="#f59e0b")
        self.clean_btn.config(state="disabled")
        
        # Run in separate thread to keep GUI responsive
        def worker():
            self.organize_files()
            self.root.after(0, lambda: self.clean_btn.config(state="normal"))
            self.root.after(0, lambda: self.status_label.config(text="⏸ IDLE", fg=COLOR_TEXT_DIM))
        
        threading.Thread(target=worker, daemon=True).start()
    
    # ========== UTILITY FUNCTIONS ==========
    def browse_directory(self):
        """Directory selection dialog"""
        directory = filedialog.askdirectory(initialdir=self.target_dir)
        if directory:
            self.target_dir = directory
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)
            self.log_message(f"📂 Target changed to: {directory}", "INFO")
    
    def log_message(self, message, level="INFO"):
        """Thread-safe logging to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.log_console.config(state="normal")
            self.log_console.insert(tk.END, log_entry, level)
            self.log_console.see(tk.END)
            self.log_console.config(state="disabled")
        
        # Schedule GUI update from main thread
        self.root.after(0, update_log)
    
    def clear_log(self):
        """Clear console log"""
        self.log_console.config(state="normal")
        self.log_console.delete(1.0, tk.END)
        self.log_console.config(state="disabled")
        self.log_message("🗑 Log cleared", "INFO")
    
    def update_time(self):
        """Update status bar time"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"🕒 {current_time}")
        self.root.after(1000, self.update_time)
    
    def show_statistics(self):
        """Display file organization statistics"""
        target_path = Path(self.path_entry.get())
        
        if not target_path.exists():
            messagebox.showerror("Error", "Target directory does not exist!")
            return
        
        stats = {}
        total_files = 0
        total_size = 0
        
        # Scan organized folders
        for category in self.file_categories.keys():
            cat_path = target_path / category
            if cat_path.exists():
                file_count = sum(1 for _ in cat_path.rglob("*") if _.is_file())
                folder_size = sum(f.stat().st_size for f in cat_path.rglob("*") if f.is_file())
                stats[category] = {"count": file_count, "size": folder_size}
                total_files += file_count
                total_size += folder_size
        
        # Format statistics
        stats_text = f"📊 FLASH FILE MANAGER STATISTICS\n{'='*50}\n\n"
        stats_text += f"📁 Target Directory: {target_path}\n"
        stats_text += f"📦 Total Files Organized: {total_files}\n"
        stats_text += f"💾 Total Size: {self.format_size(total_size)}\n\n"
        stats_text += f"{'Category':<20} {'Files':<10} {'Size'}\n"
        stats_text += f"{'-'*50}\n"
        
        for category, data in sorted(stats.items()):
            stats_text += f"{category:<20} {data['count']:<10} {self.format_size(data['size'])}\n"
        
        # Show in popup
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Statistics")
        stats_window.geometry("600x500")
        stats_window.configure(bg=COLOR_BG)
        
        text_widget = scrolledtext.ScrolledText(
            stats_window, font=("Consolas", 10), bg="#0f172a", fg=COLOR_TEXT,
            bd=0, relief="flat", wrap="word"
        )
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert(1.0, stats_text)
        text_widget.config(state="disabled")
    
    def format_size(self, size_bytes):
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

# ========== APPLICATION ENTRY POINT ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = FlashFileManager(root)
    root.mainloop()