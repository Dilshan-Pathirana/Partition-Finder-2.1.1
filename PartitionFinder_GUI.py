#!/usr/bin/env python3
"""
PartitionFinder GUI - Simple interface for running PartitionFinder analysis
"""

import sys
import os
import shutil
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from partitionfinder.core import run_folder


class PartitionFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PartitionFinder - GUI")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.nexus_path = tk.StringVar()
        self.cfg_path = tk.StringVar()
        self.is_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="PartitionFinder Analysis", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # NEXUS file selection
        ttk.Label(main_frame, text="NEXUS Alignment File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.nexus_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_nexus).grid(row=1, column=2, padx=5)
        
        # Config file selection
        ttk.Label(main_frame, text="Configuration File (.cfg):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.cfg_path, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_cfg).grid(row=2, column=2, padx=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.run_button = ttk.Button(button_frame, text="Run Analysis", command=self.run_analysis)
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Output log
        log_frame = ttk.LabelFrame(main_frame, text="Analysis Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_nexus(self):
        filename = filedialog.askopenfilename(
            title="Select NEXUS Alignment File",
            filetypes=[("NEXUS files", "*.nexus *.nex"), ("All files", "*.*")]
        )
        if filename:
            self.nexus_path.set(filename)
            
    def browse_cfg(self):
        filename = filedialog.askopenfilename(
            title="Select Configuration File",
            filetypes=[("Config files", "*.cfg"), ("All files", "*.*")]
        )
        if filename:
            self.cfg_path.set(filename)
            
    def clear_fields(self):
        self.nexus_path.set("")
        self.cfg_path.set("")
        self.log_text.delete(1.0, tk.END)
        self.status_label.config(text="Ready")
        
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def run_analysis(self):
        if self.is_running:
            messagebox.showwarning("Analysis Running", "An analysis is already in progress.")
            return
            
        # Validate inputs
        nexus_file = self.nexus_path.get().strip()
        cfg_file = self.cfg_path.get().strip()
        
        if not nexus_file or not cfg_file:
            messagebox.showerror("Error", "Please select both NEXUS and configuration files.")
            return
            
        if not os.path.exists(nexus_file):
            messagebox.showerror("Error", f"NEXUS file not found:\n{nexus_file}")
            return
            
        if not os.path.exists(cfg_file):
            messagebox.showerror("Error", f"Configuration file not found:\n{cfg_file}")
            return
        
        # Run analysis in separate thread
        self.is_running = True
        self.run_button.config(state='disabled')
        self.status_label.config(text="Analysis in progress...")
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self._run_analysis_thread, args=(nexus_file, cfg_file))
        thread.daemon = True
        thread.start()
        
    def _run_analysis_thread(self, nexus_file, cfg_file):
        try:
            # Create output directory
            nexus_basename = os.path.splitext(os.path.basename(nexus_file))[0]
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, "examples", "results", f"{nexus_basename}_results")
            
            # Create the output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            self.log(f"Creating analysis directory: {output_dir}")
            
            # Copy files to output directory
            nexus_dest = os.path.join(output_dir, os.path.basename(nexus_file))
            cfg_dest = os.path.join(output_dir, "partition_finder.cfg")
            
            shutil.copy2(nexus_file, nexus_dest)
            shutil.copy2(cfg_file, cfg_dest)
            
            self.log(f"Copied files to analysis directory")
            
            # Update config file to point to the copied nexus file
            with open(cfg_dest, 'r') as f:
                cfg_content = f.read()
            
            # Replace alignment path in config
            cfg_content = re.sub(
                r'alignment\s*=\s*[^;]+;',
                f'alignment = {os.path.basename(nexus_file)};',
                cfg_content
            )
            
            with open(cfg_dest, 'w') as f:
                f.write(cfg_content)
            
            self.log(f"Updated configuration file")
            self.log(f"\n{'='*60}")
            self.log(f"Starting PartitionFinder analysis...")
            self.log(f"Results will be saved in: {os.path.join(output_dir, 'analysis')}")
            self.log(f"{'='*60}\n")
            
            try:
                result = run_folder(output_dir, datatype="DNA", passed_args=["--no-ml-tree"], name="PartitionFinder")
                
                if result == 0 or result is None:
                    self.log(f"\n{'='*60}")
                    self.log("✓ Analysis completed successfully!")
                    self.log(f"{'='*60}\n")
                    self.log(f"Results location: {os.path.join(output_dir, 'analysis')}")
                    
                    self.root.after(0, lambda: self.status_label.config(text="Analysis completed successfully!"))
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Success", 
                        f"Analysis completed!\n\nResults saved in:\n{os.path.join(output_dir, 'analysis')}"
                    ))
                else:
                    self.log(f"\nAnalysis finished with return code: {result}")
                    self.root.after(0, lambda: self.status_label.config(text="Analysis completed with warnings"))
                    
            except SystemExit as e:
                code = e.code if e.code is not None else 0
                if code == 0:
                    self.log(f"\n{'='*60}")
                    self.log("✓ Analysis completed!")
                    self.log(f"{'='*60}\n")
                    self.root.after(0, lambda: self.status_label.config(text="Analysis completed"))
                else:
                    self.log(f"\nAnalysis exited with code: {code}")
                    self.root.after(0, lambda: self.status_label.config(text=f"Analysis failed (code {code})"))
                    
            except Exception as e:
                self.log(f"\n✗ Error during analysis: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
                self.root.after(0, lambda: self.status_label.config(text="Analysis failed"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed:\n{str(e)}"))
                
            finally:
                pass
                
        except Exception as e:
            self.log(f"\n✗ Setup error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Setup failed:\n{str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="Setup failed"))
            
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.run_button.config(state='normal'))


def main():
    root = tk.Tk()
    app = PartitionFinderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
