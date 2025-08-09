#!/usr/bin/env python3
"""
Ableton VST Audit Tool
Scans Ableton Live .als project files to extract VST plugin usage information.
Supports both GUI and command-line interfaces.
"""

import os
import sys
import gzip
import xml.etree.ElementTree as ET
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from collections import Counter, defaultdict
from datetime import datetime
import threading


class AbletonVSTAuditor:
    def __init__(self):
        self.vst_usage = Counter()
        self.project_vsts = defaultdict(list)
        self.vst_manufacturers = {}  # VST name -> manufacturer mapping
        self.processed_files = 0
        self.total_files = 0
        self.current_file = ""
        self.progress_callback = None
        
    def find_als_files(self, directory):
        """Recursively find all .als files in the given directory."""
        als_files = []
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.als'):
                        als_files.append(os.path.join(root, file))
        except (OSError, PermissionError) as e:
            print(f"Error accessing directory {directory}: {e}")
        return als_files
    
    def extract_manufacturer_from_path(self, dll_path):
        """Extract manufacturer name from DLL file path."""
        if not dll_path:
            return None
            
        # Common folder names to skip
        skip_folders = {
            'vst', 'vst2', 'vst3', '_effects', '_effects 2', 'effects', 'mastering', 
            'reverb', 'distortion', 'slowmo', 'delay', 'compression', 'eq', 'modulation',
            'd:', 'c:', 'program files', 'program files (x86)', 'x64', 'x86', 'plugins',
            'steinberg', 'vstplugins', '64-bit', '32-bit'
        }
        
        path_parts = dll_path.replace('\\', '/').split('/')
        
        # Look for manufacturer names in path (usually in folder names before the DLL)
        for i, part in enumerate(path_parts):
            if part.lower().endswith('.dll'):
                # Check the folders before the DLL
                for j in range(i-1, -1, -1):
                    folder = path_parts[j].strip()
                    if folder and folder.lower() not in skip_folders and len(folder) > 2:
                        return folder
                break
        
        return None
    
    def get_manufacturer_from_plugin_name(self, plugin_name):
        """Get manufacturer from plugin name using known patterns and databases."""
        if not plugin_name:
            return None
            
        plugin_lower = plugin_name.lower()
        
        # Known manufacturer patterns
        manufacturer_patterns = {
            'tal-': 'TAL-Software',
            'labs': 'Spitfire Audio',
            'ozone': 'iZotope',
            'levels': 'Mastering the Mix',
            'rc-20': 'XLN Audio',
            'halftime': 'Cable Guys',
            'blackhole': 'Eventide',
            'decapitator': 'Soundtoys',
            'waveshell': 'Waves',
            '2getheraudio': '2getheraudio',
            'cherry': 'Cherry Audio'
        }
        
        for pattern, manufacturer in manufacturer_patterns.items():
            if pattern in plugin_lower:
                return manufacturer
        
        return None
    
    def parse_als_file(self, file_path):
        """Parse an .als file and extract VST information."""
        vsts_found = []
        local_manufacturers = {}
        
        try:
            with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
                content = f.read()
                root = ET.fromstring(content)
                
                # Search all elements for VST DLL references
                for elem in root.iter():
                    # Check element text content
                    if elem.text and '.dll' in elem.text.lower():
                        dll_path = elem.text.strip()
                        dll_name = os.path.basename(dll_path)
                        if dll_name and dll_name not in vsts_found:
                            vsts_found.append(dll_name)
                            # Extract manufacturer from path
                            manufacturer = self.extract_manufacturer_from_path(dll_path)
                            if manufacturer and dll_name not in local_manufacturers:
                                local_manufacturers[dll_name] = manufacturer
                    
                    # Check all attributes for DLL paths
                    for attr_name, attr_value in elem.attrib.items():
                        if attr_value and '.dll' in attr_value.lower():
                            dll_path = attr_value.strip()
                            dll_name = os.path.basename(dll_path)
                            if dll_name and dll_name not in vsts_found:
                                vsts_found.append(dll_name)
                                # Extract manufacturer from path
                                manufacturer = self.extract_manufacturer_from_path(dll_path)
                                if manufacturer and dll_name not in local_manufacturers:
                                    local_manufacturers[dll_name] = manufacturer
                    
                    # Check BrowserContentPath for manufacturer info (format: query:Plugins#VST:Manufacturer:PluginName)
                    if elem.tag == 'BrowserContentPath':
                        value_elem = elem.find('Value')
                        if value_elem is not None and value_elem.text:
                            browser_path = value_elem.text
                            if 'Plugins#VST' in browser_path and ':' in browser_path:
                                parts = browser_path.split(':')
                                if len(parts) >= 4:  # query:Plugins#VST:Manufacturer:PluginName
                                    manufacturer = parts[2].replace('%20', ' ')  # URL decode spaces
                                    plugin_name = parts[3].replace('%20', ' ')
                                    # Find matching VST and associate manufacturer
                                    for vst in vsts_found:
                                        if plugin_name.lower() in vst.lower() or vst.lower() in plugin_name.lower():
                                            local_manufacturers[vst] = manufacturer
                    
                    # Special handling for plugin name elements
                    if elem.tag in ['VstPluginInfo', 'Vst3PluginInfo', 'PluginDesc']:
                        # Look for Name attribute or child elements
                        name = elem.get('Name')
                        if name and name not in vsts_found and not name.endswith('.dll'):
                            vsts_found.append(name)
                        
                        # Check child elements for plugin names
                        for child in elem:
                            if child.text and not child.text.endswith('.dll') and len(child.text) < 100:
                                plugin_name = child.text.strip()
                                if plugin_name and plugin_name not in vsts_found:
                                    vsts_found.append(plugin_name)
                
                # Update global manufacturer mapping, trying multiple methods
                for vst in vsts_found:
                    if vst not in self.vst_manufacturers:
                        # Try different methods to find manufacturer
                        manufacturer = (
                            local_manufacturers.get(vst) or  # From path
                            self.get_manufacturer_from_plugin_name(vst) or  # From name patterns
                            "Unknown"
                        )
                        self.vst_manufacturers[vst] = manufacturer
                
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return list(set(vsts_found))  # Remove duplicates
    
    def update_progress(self, message):
        """Update progress if callback is set."""
        if self.progress_callback:
            self.progress_callback(message)
    
    def scan_directory(self, directory):
        """Scan directory for .als files and extract VST information."""
        self.vst_usage.clear()
        self.project_vsts.clear()
        self.processed_files = 0
        
        self.update_progress("Finding .als files...")
        als_files = self.find_als_files(directory)
        self.total_files = len(als_files)
        
        if not als_files:
            self.update_progress("No .als files found in directory")
            return
        
        self.update_progress(f"Found {self.total_files} .als files. Starting scan...")
        
        for file_path in als_files:
            self.current_file = os.path.basename(file_path)
            self.update_progress(f"Processing: {self.current_file}")
            
            vsts = self.parse_als_file(file_path)
            
            if vsts:
                self.project_vsts[file_path] = vsts
                for vst in vsts:
                    self.vst_usage[vst] += 1
            
            self.processed_files += 1
            
        self.update_progress(f"Scan complete! Found {len(self.vst_usage)} unique VSTs")
    
    def generate_report(self, output_file):
        """Generate a detailed report of VST usage."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("ABLETON VST AUDIT REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Projects Scanned: {len(self.project_vsts)}\n")
            f.write(f"Total Unique VSTs Found: {len(self.vst_usage)}\n\n")
            
            if self.vst_usage:
                f.write("VST USAGE SUMMARY (by frequency)\n")
                f.write("-" * 40 + "\n")
                for vst, count in self.vst_usage.most_common():
                    manufacturer = self.vst_manufacturers.get(vst, "Unknown")
                    f.write(f"{count:3d}x  {vst:<35} [{manufacturer}]\n")
                
                f.write("\n\nVSTS BY MANUFACTURER\n")
                f.write("-" * 30 + "\n")
                # Group VSTs by manufacturer
                by_manufacturer = defaultdict(list)
                for vst in self.vst_usage.keys():
                    manufacturer = self.vst_manufacturers.get(vst, "Unknown")
                    by_manufacturer[manufacturer].append((vst, self.vst_usage[vst]))
                
                for manufacturer in sorted(by_manufacturer.keys()):
                    f.write(f"\n{manufacturer}:\n")
                    vst_list = sorted(by_manufacturer[manufacturer], key=lambda x: x[0])
                    for vst, count in vst_list:
                        f.write(f"  • {vst} ({count}x)\n")
                
                f.write("\n\nALPHABETICAL VST LIST\n")
                f.write("-" * 30 + "\n")
                for vst in sorted(self.vst_usage.keys()):
                    manufacturer = self.vst_manufacturers.get(vst, "Unknown")
                    f.write(f"• {vst:<35} [{manufacturer}]\n")
                
                f.write("\n\nPROJECT BREAKDOWN\n")
                f.write("-" * 25 + "\n")
                for project_path, vsts in self.project_vsts.items():
                    project_name = os.path.basename(project_path)
                    f.write(f"\n{project_name}:\n")
                    for vst in sorted(set(vsts)):
                        manufacturer = self.vst_manufacturers.get(vst, "Unknown")
                        f.write(f"  • {vst:<35} [{manufacturer}]\n")
            else:
                f.write("No VST plugins found in the scanned projects.\n")


class AbletonVSTGUI:
    def __init__(self):
        self.auditor = AbletonVSTAuditor()
        self.auditor.progress_callback = self.update_progress
        self.root = tk.Tk()
        self.setup_gui()
        self.scan_thread = None
        
    def setup_gui(self):
        """Setup the GUI interface."""
        self.root.title("Ableton VST Auditor")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Directory selection
        ttk.Label(main_frame, text="Select Ableton Projects Directory:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(0, weight=1)
        
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, state="readonly")
        self.dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(row=0, column=1)
        
        # Scan button
        self.scan_button = ttk.Button(main_frame, text="Start Scan", command=self.start_scan)
        self.scan_button.grid(row=2, column=0, pady=(0, 10))
        
        # Progress
        self.progress_var = tk.StringVar(value="Select a directory to begin")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="5")
        results_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = tk.Text(results_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Save report button
        self.save_button = ttk.Button(main_frame, text="Save Report", command=self.save_report, state="disabled")
        self.save_button.grid(row=6, column=0, pady=(0, 5))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
    
    def browse_directory(self):
        """Open directory browser dialog."""
        directory = filedialog.askdirectory(title="Select Ableton Projects Directory")
        if directory:
            self.dir_var.set(directory)
    
    def update_progress(self, message):
        """Update progress in GUI (thread-safe)."""
        self.root.after(0, lambda: self.progress_var.set(message))
    
    def start_scan(self):
        """Start scanning in a separate thread."""
        directory = self.dir_var.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory first")
            return
        
        if not os.path.exists(directory):
            messagebox.showerror("Error", "Selected directory does not exist")
            return
        
        # Disable scan button and enable progress bar
        self.scan_button.config(state="disabled")
        self.save_button.config(state="disabled")
        self.progress_bar.start()
        self.results_text.delete(1.0, tk.END)
        
        # Start scan in separate thread
        self.scan_thread = threading.Thread(target=self.run_scan, args=(directory,))
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def run_scan(self, directory):
        """Run the scan (called in separate thread)."""
        try:
            self.auditor.scan_directory(directory)
            self.root.after(0, self.scan_complete)
        except Exception as e:
            self.root.after(0, lambda: self.scan_error(str(e)))
    
    def scan_complete(self):
        """Handle scan completion (called in main thread)."""
        self.progress_bar.stop()
        self.scan_button.config(state="normal")
        self.save_button.config(state="normal")
        
        # Display results
        self.display_results()
    
    def scan_error(self, error_msg):
        """Handle scan error (called in main thread)."""
        self.progress_bar.stop()
        self.scan_button.config(state="normal")
        messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{error_msg}")
    
    def display_results(self):
        """Display scan results in the text area."""
        self.results_text.delete(1.0, tk.END)
        
        if not self.auditor.vst_usage:
            self.results_text.insert(tk.END, "No VST plugins found in the scanned projects.")
            return
        
        self.results_text.insert(tk.END, f"SCAN RESULTS\n")
        self.results_text.insert(tk.END, f"Projects scanned: {len(self.auditor.project_vsts)}\n")
        self.results_text.insert(tk.END, f"Unique VSTs found: {len(self.auditor.vst_usage)}\n\n")
        
        self.results_text.insert(tk.END, "TOP VSTs (by usage):\n")
        for i, (vst, count) in enumerate(self.auditor.vst_usage.most_common(20), 1):
            manufacturer = self.auditor.vst_manufacturers.get(vst, "Unknown")
            self.results_text.insert(tk.END, f"{i:2d}. {vst} ({count}x) [{manufacturer}]\n")
        
        if len(self.auditor.vst_usage) > 20:
            self.results_text.insert(tk.END, f"\n... and {len(self.auditor.vst_usage) - 20} more\n")
            
        # Show manufacturer summary
        manufacturer_counts = defaultdict(int)
        for vst in self.auditor.vst_usage.keys():
            manufacturer = self.auditor.vst_manufacturers.get(vst, "Unknown")
            manufacturer_counts[manufacturer] += 1
        
        self.results_text.insert(tk.END, f"\nMANUFACTURERS FOUND:\n")
        for manufacturer, count in sorted(manufacturer_counts.items(), key=lambda x: -x[1]):
            self.results_text.insert(tk.END, f"• {manufacturer}: {count} plugin(s)\n")
    
    def save_report(self):
        """Save detailed report to file."""
        if not self.auditor.vst_usage:
            messagebox.showwarning("Warning", "No results to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save VST Audit Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.auditor.generate_report(file_path)
                messagebox.showinfo("Success", f"Report saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report:\n{e}")
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Ableton VST Auditor")
    parser.add_argument("--cli", action="store_true", help="Use command-line interface")
    parser.add_argument("directory", nargs="?", help="Directory to scan (CLI mode)")
    parser.add_argument("--output", "-o", default="vst_audit_report.txt", help="Output file (CLI mode)")
    
    args = parser.parse_args()
    
    if args.cli:
        if not args.directory:
            print("Error: Directory argument required in CLI mode")
            parser.print_help()
            return 1
        
        # Command-line mode
        auditor = AbletonVSTAuditor()
        auditor.progress_callback = lambda msg: print(msg)
        
        print(f"Scanning directory: {args.directory}")
        auditor.scan_directory(args.directory)
        
        if auditor.vst_usage:
            print(f"\nGenerating report: {args.output}")
            auditor.generate_report(args.output)
            print(f"Found {len(auditor.vst_usage)} unique VSTs across {len(auditor.project_vsts)} projects")
        else:
            print("No VST plugins found.")
        
        return 0
    else:
        # GUI mode
        app = AbletonVSTGUI()
        app.run()
        return 0


if __name__ == "__main__":
    sys.exit(main())