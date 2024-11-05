import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import keyboard
from datetime import time
from config import load_settings, save_settings

class AutoTyperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Typer")
        self.root.minsize(600, 400)
        
        # Configure Thai font
        self.text_font = ('Cordia New', 16)  # Explicitly use Cordia New for Thai support
        
        self.settings = load_settings()
        self.auto_typer = None  # Will be initialized later
        self.recording_hotkey = False
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text input
        text_frame = ttk.LabelFrame(main_frame, text="Text Input", padding="5")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=10, 
                                                 font=self.text_font)  # Use Cordia New font
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="5")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # WPM control
        ttk.Label(control_frame, text="WPM:").grid(row=0, column=0, padx=5)
        self.wpm_var = tk.StringVar(value=str(self.settings.get("wpm", 60)))
        ttk.Entry(control_frame, textvariable=self.wpm_var, width=10).grid(row=0, column=1)
        
        # Random delay
        self.random_delay_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Random Delay", variable=self.random_delay_var).grid(row=0, column=2, padx=5)
        
        # Delay settings
        ttk.Label(control_frame, text="Min (ms):").grid(row=0, column=3)
        self.min_delay_var = tk.StringVar(value="100")
        ttk.Entry(control_frame, textvariable=self.min_delay_var, width=8).grid(row=0, column=4)
        
        ttk.Label(control_frame, text="Max (ms):").grid(row=0, column=5)
        self.max_delay_var = tk.StringVar(value="1000")
        ttk.Entry(control_frame, textvariable=self.max_delay_var, width=8).grid(row=0, column=6)
        
        # Hotkey settings
        hotkey_frame = ttk.LabelFrame(main_frame, text="Hotkey Settings", padding="5")
        hotkey_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start/Stop hotkey
        ttk.Label(hotkey_frame, text="Start/Stop:").grid(row=0, column=0, padx=5)
        self.start_stop_key = tk.StringVar(value=self.settings["hotkeys"]["start_stop"])
        self.start_stop_btn = ttk.Button(hotkey_frame, textvariable=self.start_stop_key, 
                                       command=lambda: self.record_hotkey("start_stop"))
        self.start_stop_btn.grid(row=0, column=1, padx=5)
        
        # Emergency stop hotkey
        ttk.Label(hotkey_frame, text="Emergency Stop:").grid(row=0, column=2, padx=5)
        self.emergency_key = tk.StringVar(value=self.settings["hotkeys"]["emergency_stop"])
        self.emergency_btn = ttk.Button(hotkey_frame, textvariable=self.emergency_key,
                                      command=lambda: self.record_hotkey("emergency_stop"))
        self.emergency_btn.grid(row=0, column=3, padx=5)
        
        # Start/Stop buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=1, column=0, columnspan=7, pady=5)
        
        self.start_btn = ttk.Button(btn_frame, text=f"Start ({self.start_stop_key.get()})", 
                                  command=self.toggle_typing)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text=f"Emergency Stop ({self.emergency_key.get()})", 
                                 command=self.emergency_stop)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Delete button
        self.delete_btn = ttk.Button(btn_frame, text="Delete Text", 
                                   command=self.clear_text)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5)
        
        # Set up hotkeys
        self.bind_hotkeys()

    def clear_text(self):
        """Clear all text from the text area."""
        self.text_area.delete("1.0", tk.END)
        self.status_var.set("Text cleared")

    def bind_hotkeys(self):
        try:
            keyboard.unhook_all()  # Clear existing hotkeys
            keyboard.on_press_key(self.start_stop_key.get(), lambda _: self.toggle_typing())
            keyboard.on_press_key(self.emergency_key.get(), lambda _: self.emergency_stop())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to bind hotkey: {str(e)}")

    def record_hotkey(self, key_type):
        if self.recording_hotkey:
            return
            
        self.recording_hotkey = True
        original_text = self.start_stop_key.get() if key_type == "start_stop" else self.emergency_key.get()
        btn = self.start_stop_btn if key_type == "start_stop" else self.emergency_btn
        
        def on_key(event):
            if event.name not in ['shift', 'ctrl', 'alt']:
                if key_type == "start_stop":
                    self.start_stop_key.set(event.name)
                    self.start_btn.config(text=f"Start ({event.name})")
                else:
                    self.emergency_key.set(event.name)
                    self.stop_btn.config(text=f"Emergency Stop ({event.name})")
                
                # Update settings
                self.settings["hotkeys"][key_type] = event.name
                save_settings(self.settings)
                
                # Rebind hotkeys
                self.bind_hotkeys()
                
                # Reset button text and state
                btn.config(state='normal')
                self.recording_hotkey = False
                keyboard.unhook(hook)
            
        # Change button text to indicate recording
        btn.config(text="Press a key...", state='disabled')
        hook = keyboard.on_press(on_key)

    def toggle_typing(self):
        if not hasattr(self, 'auto_typer') or not self.auto_typer or not self.auto_typer.is_running():
            self.start_typing()
        else:
            self.stop_typing()

    def start_typing(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Error", "No text to type!")
            return

        try:
            if not self.auto_typer:
                from auto_typer import AutoTyper
                self.auto_typer = AutoTyper()
            
            self.auto_typer.set_text(text)
            self.auto_typer.set_wpm(int(self.wpm_var.get()))
            self.auto_typer.set_random_delay(
                self.random_delay_var.get(),
                float(self.min_delay_var.get()),
                float(self.max_delay_var.get())
            )
            
            self.auto_typer.set_status_callback(lambda s: self.status_var.set(s))
            self.auto_typer.set_progress_callback(self.update_progress)
            
            self.auto_typer.start()
            self.start_btn.config(text=f"Stop ({self.start_stop_key.get()})")
            self.status_var.set("Typing started")

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def stop_typing(self):
        if self.auto_typer:
            self.auto_typer.stop()
            self.start_btn.config(text=f"Start ({self.start_stop_key.get()})")
            self.status_var.set("Stopped")

    def emergency_stop(self):
        if self.auto_typer:
            self.auto_typer.stop()
            self.start_btn.config(text=f"Start ({self.start_stop_key.get()})")
            self.status_var.set("Emergency stop activated")

    def update_progress(self, current: int, total: int):
        progress = (current / total * 100) if total > 0 else 0
        self.progress_var.set(progress)
