"""
PartitionFinder GUI Application
A user-friendly graphical interface for phylogenetic partition analysis
"""
import sys
import os
import threading
import subprocess
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import shutil

class PartitionFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PartitionFinder 2.1.1 - Python 3 Edition")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)

        # Variables
        self.cfg_file = tk.StringVar()
        self.alignment_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.analysis_type = tk.StringVar(value="DNA")
        self.is_running = False
        self.process = None

        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        """Configure modern styles for the application"""
        # Modern Color Palette
        self.colors = {
            "bg": "#1E1E1E",              # Dark background
            "bg_light": "#2D2D2D",        # Lighter dark
            "bg_card": "#252526",         # Card background
            "fg": "#FFFFFF",              # White text
            "fg_secondary": "#CCCCCC",    # Gray text
            "primary": "#0E7490",         # Cyan blue
            "primary_hover": "#0891B2",   # Lighter cyan
            "secondary": "#6B7280",       # Gray
            "success": "#10B981",         # Green
            "warning": "#F59E0B",         # Orange
            "error": "#EF4444",           # Red
            "info": "#3B82F6",            # Blue
            "accent": "#8B5CF6"           # Purple
        }

        self.root.configure(bg=self.colors["bg"])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure frame styles
        style.configure("Card.TFrame", 
                       background=self.colors["bg_card"],
                       relief="flat")
        
        style.configure("Main.TFrame",
                       background=self.colors["bg"])
        
        # Configure label styles
        style.configure("Title.TLabel",
                       background=self.colors["bg"],
                       foreground=self.colors["fg"],
                       font=("Segoe UI", 20, "bold"))
        
        style.configure("Subtitle.TLabel",
                       background=self.colors["bg"],
                       foreground=self.colors["fg_secondary"],
                       font=("Segoe UI", 10))
        
        style.configure("CardTitle.TLabel",
                       background=self.colors["bg_card"],
                       foreground=self.colors["fg"],
                       font=("Segoe UI", 11, "bold"))
        
        style.configure("Hint.TLabel",
                       background=self.colors["bg_card"],
                       foreground=self.colors["fg_secondary"],
                       font=("Segoe UI", 9))
        
        # Configure button styles with larger size
        style.configure("Accent.TButton",
                       background=self.colors["primary"],
                       foreground=self.colors["fg"],
                       borderwidth=0,
                       focuscolor=self.colors["primary"],
                       font=("Segoe UI", 11, "bold"),
                       padding=(20, 12))
        
        style.map("Accent.TButton",
                 background=[("active", self.colors["primary_hover"]),
                           ("pressed", self.colors["primary"])])
        
        style.configure("Stop.TButton",
                       background=self.colors["error"],
                       foreground=self.colors["fg"],
                       borderwidth=0,
                       font=("Segoe UI", 11, "bold"),
                       padding=(20, 12))
        
        style.map("Stop.TButton",
                 background=[("active", "#DC2626")])
        
        style.configure("Secondary.TButton",
                       background=self.colors["secondary"],
                       foreground=self.colors["fg"],
                       borderwidth=0,
                       font=("Segoe UI", 10),
                       padding=(15, 8))
        
        style.map("Secondary.TButton",
                 background=[("active", "#4B5563")])
        
        # Configure radiobutton styles
        style.configure("Analysis.TRadiobutton",
                       background=self.colors["bg_card"],
                       foreground=self.colors["fg"],
                       font=("Segoe UI", 10, "bold"),
                       indicatorcolor=self.colors["primary"],
                       borderwidth=2,
                       relief="flat")
        
        # Configure entry styles
        style.configure("Modern.TEntry",
                       fieldbackground=self.colors["bg_light"],
                       foreground=self.colors["fg"],
                       borderwidth=1,
                       relief="flat",
                       font=("Segoe UI", 10))
        
        # Configure labelframe styles
        style.configure("Card.TLabelframe",
                       background=self.colors["bg_card"],
                       foreground=self.colors["fg"],
                       borderwidth=0,
                       relief="flat",
                       font=("Segoe UI", 11, "bold"))
        
        style.configure("Card.TLabelframe.Label",
                       background=self.colors["bg_card"],
                       foreground=self.colors["primary"],
                       font=("Segoe UI", 12, "bold"))

        # Style Configuration
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass  # Fallback to default theme if 'clam' is not available

        # General Styles
        style.configure(".",
                        background=self.colors["bg"],
                        foreground=self.colors["fg"],
                        font=("Segoe UI", 10))

        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"])
        style.configure("TRadiobutton",
                        background=self.colors["bg_light"],
                        foreground=self.colors["fg"],
                        indicatorbackground=self.colors["secondary"],
                        indicatormargin=5)
        style.map("TRadiobutton",
                  background=[('active', self.colors["secondary"])])

        # LabelFrame Style
        style.configure("TLabelFrame",
                        background=self.colors["bg_light"],
                        foreground=self.colors["fg"],
                        labelmargins=(10, 5),
                        borderwidth=1,
                        relief="solid")
        style.configure("TLabelFrame.Label",
                        background=self.colors["bg_light"],
                        foreground=self.colors["fg"],
                        font=("Segoe UI", 11, "bold"))

        # Button Styles
        style.configure("TButton",
                        font=("Segoe UI", 11, "bold"),
                        padding=(15, 10),
                        borderwidth=0,
                        anchor="center")
        style.map("TButton",
                  background=[('!active', self.colors["secondary"]), ('active', self.colors["primary_hover"])],
                  foreground=[('!disabled', self.colors["fg"])])

        # Primary Button (Start)
        style.configure("Primary.TButton",
                        background=self.colors["primary"],
                        foreground=self.colors["fg"])
        style.map("Primary.TButton",
                  background=[('!active', self.colors["primary"]), ('active', self.colors["primary_hover"])])

        # Stop Button
        style.configure("Stop.TButton",
                        background=self.colors["error"],
                        foreground=self.colors["fg"])
        style.map("Stop.TButton",
                  background=[('!active', self.colors["error"]), ('active', "#E84A5F")])

        # Entry (Readonly)
        style.configure("TEntry",
                        fieldbackground="#4A4A4A",
                        foreground=self.colors["fg"],
                        borderwidth=1,
                        relief="solid",
                        padding=5)
        style.map("TEntry",
                  bordercolor=[('focus', self.colors["primary"])])

        # Progress Bar
        style.configure("TProgressbar",
                        troughcolor=self.colors["secondary"],
                        background=self.colors["primary"])

    def setup_ui(self):
        """Create the user interface with modern styling"""
        # Main container with style
        main_frame = ttk.Frame(self.root, padding="25", style="Main.TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Header Section with gradient effect
        header_frame = tk.Frame(main_frame, bg=self.colors["bg"], height=80)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="🧬 PartitionFinder 2.1.1", style="Title.TLabel")
        title_label.grid(row=0, column=0, sticky="w", padx=5)
        
        subtitle = ttk.Label(header_frame, text="Modern Phylogenetic Partition Analysis Tool", 
                            style="Subtitle.TLabel")
        subtitle.grid(row=1, column=0, sticky="w", padx=5, pady=(5, 0))
        
        # Analysis Type Section (Card Style)
        type_frame = ttk.LabelFrame(main_frame, text="  Analysis Type  ", 
                                    padding="20", style="Card.TLabelframe")
        type_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        # Create styled radio buttons with larger size
        dna_rb = ttk.Radiobutton(type_frame, text="🔬 DNA Sequences", 
                                variable=self.analysis_type, value="DNA", 
                                style="Analysis.TRadiobutton")
        dna_rb.pack(side=tk.LEFT, padx=15, pady=5)
        
        protein_rb = ttk.Radiobutton(type_frame, text="🧪 Protein Sequences", 
                                    variable=self.analysis_type, value="Protein",
                                    style="Analysis.TRadiobutton")
        protein_rb.pack(side=tk.LEFT, padx=15, pady=5)
        
        morph_rb = ttk.Radiobutton(type_frame, text="📊 Morphology Data", 
                                  variable=self.analysis_type, value="Morphology",
                                  style="Analysis.TRadiobutton")
        morph_rb.pack(side=tk.LEFT, padx=15, pady=5)
        
        # File Selection Section (Card Style)
        file_frame = ttk.LabelFrame(main_frame, text="  Input & Output Files  ", 
                                    padding="20", style="Card.TLabelframe")
        file_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        # Config File
        row = 0
        ttk.Label(file_frame, text="📄 Configuration File:", style="CardTitle.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=10, padx=8)
        ttk.Entry(file_frame, textvariable=self.cfg_file, state="readonly", 
                 style="Modern.TEntry", font=("Segoe UI", 10)).grid(
            row=row, column=1, sticky="ew", padx=12, pady=10)
        ttk.Button(file_frame, text="📁 Browse", command=self.browse_cfg,
                  style="Secondary.TButton").grid(row=row, column=2, pady=10, padx=8)
        
        # Alignment File
        row += 1
        ttk.Label(file_frame, text="🧬 Alignment File:", style="CardTitle.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=10, padx=8)
        ttk.Entry(file_frame, textvariable=self.alignment_file, state="readonly",
                 style="Modern.TEntry", font=("Segoe UI", 10)).grid(
            row=row, column=1, sticky="ew", padx=12, pady=10)
        ttk.Button(file_frame, text="📁 Browse", command=self.browse_alignment,
                  style="Secondary.TButton").grid(row=row, column=2, pady=10, padx=8)
        
        # File format hint
        row += 1
        hint = ttk.Label(file_frame, text="✓ Supported: .nexus, .nex, .phy (NEXUS auto-converts)", 
                        style="Hint.TLabel")
        hint.grid(row=row, column=1, sticky=tk.W, padx=12, pady=(0, 5))
        
        # Output Directory
        row += 1
        ttk.Label(file_frame, text="💾 Output Location:", style="CardTitle.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=10, padx=8)
        ttk.Entry(file_frame, textvariable=self.output_dir, state="readonly",
                 style="Modern.TEntry", font=("Segoe UI", 10)).grid(
            row=row, column=1, sticky="ew", padx=12, pady=10)
        ttk.Button(file_frame, text="📁 Browse", command=self.browse_output,
                  style="Secondary.TButton").grid(row=row, column=2, pady=10, padx=8)
        
        # Action Buttons (Large & Prominent)
        button_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.analyze_btn = ttk.Button(button_frame, text="▶  START ANALYSIS", 
                                     command=self.start_analysis, style="Accent.TButton")
        self.analyze_btn.pack(side=tk.LEFT, padx=8)
        
        self.stop_btn = ttk.Button(button_frame, text="⬛  STOP", 
                                  command=self.stop_analysis, state="disabled", 
                                  style="Stop.TButton")
        self.stop_btn.pack(side=tk.LEFT, padx=8)
        
        ttk.Button(button_frame, text="🗑  Clear Logs", command=self.clear_logs,
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=8)
        
        # Progress Bar (Modern style)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        # Log Display (Card Style with dark theme)
        log_frame = ttk.LabelFrame(main_frame, text="  Analysis Log & Debug Info  ", 
                                   padding="15", style="Card.TLabelframe")
        log_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(0, 15))
        main_frame.rowconfigure(5, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=16, wrap=tk.WORD, font=("Cascadia Code", 9),
            bg="#0D1117", fg="#C9D1D9",
            relief="flat", borderwidth=0,
            insertbackground="#58A6FF",
            selectbackground="#1F6FEB",
            selectforeground="#FFFFFF"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status Bar (Modern)
        status_frame = tk.Frame(main_frame, bg=self.colors["bg_card"], height=35)
        status_frame.grid(row=6, column=0, columnspan=3, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = tk.Label(status_frame, text="🟢 Ready", 
                                     bg=self.colors["bg_card"], 
                                     fg=self.colors["success"],
                                     font=("Segoe UI", 10, "bold"),
                                     anchor="w", padx=15, pady=8)
        self.status_label.pack(fill=tk.X)
        
        # Configure tags for colored logs
        self.log_text.tag_config("INFO", foreground="#58A6FF")      # Blue
        self.log_text.tag_config("WARNING", foreground="#D29922")   # Orange
        self.log_text.tag_config("ERROR", foreground="#F85149")     # Red
        self.log_text.tag_config("SUCCESS", foreground="#3FB950")   # Green
        
        self.log("🚀 Application initialized successfully", "SUCCESS")

    def browse_cfg(self):
        """Browse for config file"""
        filename = filedialog.askopenfilename(
            title="Select Configuration File",
            filetypes=[("Config files", "*.cfg"), ("All files", "*.* אמיתי")]
        )
        if filename:
            self.cfg_file.set(filename)
            self.log(f"Config file selected: {os.path.basename(filename)}", "INFO")
            
            # Auto-detect alignment file from config
            self.auto_detect_alignment(filename)
    
    def auto_detect_alignment(self, cfg_path):
        """Read config file and auto-detect alignment file"""
        try:
            with open(cfg_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('alignment'):
                        # Extract filename: "alignment = filename.phy;"
                        parts = line.split('=')
                        if len(parts) == 2:
                            align_file = parts[1].strip().rstrip(';').strip()
                            # Make it relative to config file directory
                            cfg_dir = os.path.dirname(cfg_path)
                            full_path = os.path.join(cfg_dir, align_file)
                            if os.path.exists(full_path):
                                self.alignment_file.set(full_path)
                                self.log(f"Auto-detected alignment: {align_file}", "INFO")
                            break
        except Exception as e:
            self.log(f"Could not auto-detect alignment: {e}", "WARNING")
    
    def browse_alignment(self):
        """Browse for alignment file"""
        filename = filedialog.askopenfilename(
            title="Select Alignment File",
            filetypes=[
                ("Alignment files", "*.nexus *.nex *.phy"),
                ("NEXUS files", "*.nexus *.nex"),
                ("Phylip files", "*.phy"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.alignment_file.set(filename)
            self.log(f"Alignment file selected: {os.path.basename(filename)}", "INFO")
    
    def browse_output(self):
        """Browse for output directory"""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir.set(dirname)
            self.log(f"Output directory: {dirname}", "INFO")
    
    def log(self, message, level="INFO"):
        """Add message to log with timestamp and color"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add emoji prefix based on level
        emoji_map = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅"
        }
        emoji = emoji_map.get(level, "ℹ️")
        
        log_msg = f"[{timestamp}] {emoji} {level:7} | {message}\n"
        
        self.log_text.insert(tk.END, log_msg, level)
        self.log_text.see(tk.END)
        self.log_text.update()
    
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
        self.log("Logs cleared", "INFO")
    
    def validate_inputs(self):
        """Validate all required inputs"""
        if not self.cfg_file.get():
            messagebox.showerror("Error", "Please select a configuration file")
            return False
        
        if not os.path.exists(self.cfg_file.get()):
            messagebox.showerror("Error", "Configuration file does not exist")
            return False
        
        if not self.alignment_file.get():
            messagebox.showerror("Error", "Please select an alignment file")
            return False
        
        if not os.path.exists(self.alignment_file.get()):
            messagebox.showerror("Error", "Alignment file does not exist")
            return False
        
        return True
    
    def start_analysis(self):
        """Start the partition analysis"""
        if not self.validate_inputs():
            return
        
        if self.is_running:
            messagebox.showwarning("Warning", "Analysis is already running")
            return
        
        # Prepare working directory
        cfg_path = self.cfg_file.get()
        working_dir = os.path.dirname(cfg_path)
        
        # If output directory specified, create analysis folder there
        if self.output_dir.get():
            output_base = self.output_dir.get()
        else:
            output_base = working_dir
        
        self.log("="*60, "INFO")
        self.log("Starting PartitionFinder Analysis", "INFO")
        self.log(f"Analysis Type: {self.analysis_type.get()}", "INFO")
        self.log(f"Working Directory: {working_dir}", "INFO")
        self.log("="*60, "INFO")
        
        # Update UI
        self.is_running = True
        self.analyze_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress.start()
        self.status_label.config(text="🔄 Analysis in progress...", fg=self.colors["info"])
        
        # Run analysis in separate thread
        thread = threading.Thread(target=self.run_analysis, 
                                 args=(working_dir, output_base))
        thread.daemon = True
        thread.start()
    
    def run_analysis(self, working_dir, output_base):
        """Run the PartitionFinder analysis"""
        try:
            # Determine which script to run
            script_map = {
                "DNA": "PartitionFinder.py",
                "Protein": "PartitionFinderProtein.py",
                "Morphology": "PartitionFinderMorphology.py"
            }
            
            script = script_map[self.analysis_type.get()]
            script_path = os.path.join(os.path.dirname(__file__), script)
            
            # Build command
            cmd = [
                sys.executable,
                script_path,
                working_dir,
                "--force-restart"
            ]
            
            self.log(f"Command: {' '.join(cmd)}", "INFO")
            
            # Run process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output line by line
            for line in self.process.stdout:
                line = line.strip()
                if not line:
                    continue
                
                # Determine log level from message
                if "ERROR" in line:
                    level = "ERROR"
                elif "WARNING" in line:
                    level = "WARNING"
                elif "complete" in line.lower() or "finished" in line.lower():
                    level = "SUCCESS"
                else:
                    level = "INFO"
                
                self.log(line, level)
            
            # Wait for completion
            return_code = self.process.wait()
            
            if return_code == 0:
                self.log("="*60, "SUCCESS")
                self.log("Analysis completed successfully!", "SUCCESS")
                self.log("="*60, "SUCCESS")
                
                # Copy results if output directory specified
                if output_base != working_dir:
                    self.copy_results(working_dir, output_base)
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Analysis completed!\n\nResults saved to:\n{working_dir}/analysis"
                ))
            else:
                self.log(f"Analysis failed with exit code {return_code}", "ERROR")
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    "Analysis failed. Check the log for details."
                ))
        
        except Exception as e:
            self.log(f"Error during analysis: {str(e)}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Analysis error:\n{str(e)}"
            ))
        
        finally:
            self.root.after(0, self.analysis_finished)
    
    def copy_results(self, source_dir, dest_base):
        """Copy analysis results to output directory"""
        try:
            source_analysis = os.path.join(source_dir, "analysis")
            if os.path.exists(source_analysis):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_dir = os.path.join(dest_base, f"analysis_{timestamp}")
                shutil.copytree(source_analysis, dest_dir)
                self.log(f"Results copied to: {dest_dir}", "SUCCESS")
        except Exception as e:
            self.log(f"Could not copy results: {e}", "WARNING")
    
    def stop_analysis(self):
        """Stop the running analysis"""
        if self.process and self.is_running:
            self.process.terminate()
            self.log("Analysis stopped by user", "WARNING")
            self.analysis_finished()
    
    def analysis_finished(self):
        """Clean up after analysis"""
        self.is_running = False
        self.process = None
        self.analyze_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.progress.stop()
        self.status_label.config(text="🟢 Ready", fg=self.colors["success"])


def main():
    """Launch the GUI application"""
    root = tk.Tk()
    app = PartitionFinderGUI(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()