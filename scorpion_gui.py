#!/usr/bin/env python3
"""
Scorpion GUI - Graphical interface for metadata viewing and management
Uses tkinter for cross-platform GUI support
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from pathlib import Path
from typing import Dict, Any, Optional, List
from metadata_parser import MetadataParser
from metadata_modifier import MetadataModifier
from output_formatter import OutputFormatter
import threading
import json
import csv


class ScorpionGUI:
    """GUI interface for Scorpion metadata tool"""

    VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    
    def __init__(self, root: tk.Tk):
        """
        Initialize Scorpion GUI.

        Args:
            root (tk.Tk): Root tkinter window
        """
        self.root = root
        self.root.title("🦂 Scorpion - Image Metadata Manager")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        self.root.resizable(True, True)
        
        self.current_file = None
        self.current_metadata = None
        self.metadata_parser = None
        self.operation_thread = None
        
        self._create_widgets()
        self._setup_styles()

    def _setup_styles(self):
        """Configure ttk styles for better appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define colors
        bg_color = '#f0f0f0'
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelFrame', background=bg_color)
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), background=bg_color)
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'), background=bg_color)
        style.configure('TButton', font=('Arial', 9))
        style.configure('Success.TLabel', foreground='green', background=bg_color)
        style.configure('Error.TLabel', foreground='red', background=bg_color)

    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # ========== LEFT PANEL: File Selection & Actions ==========
        left_frame = ttk.LabelFrame(main_frame, text="📂 File & Actions", padding="10")
        left_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)

        # File selection button
        btn_select = ttk.Button(left_frame, text="📁 Open Image", command=self._select_file)
        btn_select.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        # Current file label
        ttk.Label(left_frame, text="Current File:", font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.file_label = ttk.Label(left_frame, text="None selected", foreground="gray", wraplength=200, justify=tk.LEFT)
        self.file_label.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # File size label
        self.size_label = ttk.Label(left_frame, text="", foreground="gray", font=('Arial', 8))
        self.size_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))

        # ========== EXTRACTION SECTION ==========
        ttk.Separator(left_frame, orient='horizontal').grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(left_frame, text="📊 Extraction", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=(5, 10))
        
        btn_refresh = ttk.Button(left_frame, text="🔍 Refresh Metadata", command=self._refresh_metadata)
        btn_refresh.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=5)

        btn_analyze = ttk.Button(left_frame, text="📈 Analyze File", command=self._analyze_file)
        btn_analyze.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=5)

        # ========== MODIFICATION SECTION ==========
        ttk.Separator(left_frame, orient='horizontal').grid(row=8, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(left_frame, text="✏️  Modifications", font=('Arial', 10, 'bold')).grid(row=9, column=0, sticky=tk.W, pady=(5, 10))

        btn_strip_exif = ttk.Button(left_frame, text="❌ Strip EXIF", command=self._strip_exif)
        btn_strip_exif.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=5)

        btn_strip_all = ttk.Button(left_frame, text="🗑️  Strip All Metadata", command=self._strip_all)
        btn_strip_all.grid(row=11, column=0, sticky=(tk.W, tk.E), pady=5)

        btn_add_comment = ttk.Button(left_frame, text="📝 Add Comment", command=self._add_comment_dialog)
        btn_add_comment.grid(row=12, column=0, sticky=(tk.W, tk.E), pady=5)

        btn_restore = ttk.Button(left_frame, text="↩️  Restore from Backup", command=self._restore_backup)
        btn_restore.grid(row=13, column=0, sticky=(tk.W, tk.E), pady=5)

        # ========== UTILITY SECTION ==========
        ttk.Separator(left_frame, orient='horizontal').grid(row=14, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(left_frame, text="🔧 Utilities", font=('Arial', 10, 'bold')).grid(row=15, column=0, sticky=tk.W, pady=(5, 10))

        btn_export_json = ttk.Button(left_frame, text="📤 Export as JSON", command=self._export_json)
        btn_export_json.grid(row=16, column=0, sticky=(tk.W, tk.E), pady=5)

        btn_export_csv = ttk.Button(left_frame, text="📊 Export as CSV", command=self._export_csv)
        btn_export_csv.grid(row=17, column=0, sticky=(tk.W, tk.E), pady=5)

        # ========== TOP RIGHT PANEL: File Info ==========
        info_frame = ttk.LabelFrame(main_frame, text="📋 File Information", padding="10")
        info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)

        # Basic info display
        self.info_text = scrolledtext.ScrolledText(info_frame, height=12, wrap=tk.WORD, font=('Courier', 9))
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.info_text.config(state=tk.DISABLED)

        # ========== BOTTOM RIGHT PANEL: Detailed Metadata ==========
        detail_frame = ttk.LabelFrame(main_frame, text="🔍 Detailed Metadata", padding="10")
        detail_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)

        # Notebook for tabs
        self.notebook = ttk.Notebook(detail_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create tabs for different metadata types
        self.tabs = {}
        for tab_name in ['EXIF', 'IPTC', 'Other']:
            frame = ttk.Frame(self.notebook)
            text_widget = scrolledtext.ScrolledText(frame, height=15, wrap=tk.WORD, font=('Courier', 8))
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.config(state=tk.DISABLED)
            self.tabs[tab_name] = text_widget
            self.notebook.add(frame, text=tab_name)

        # ========== STATUS BAR ==========
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="✅ Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))

    def _select_file(self):
        """Open file dialog to select an image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("GIF", "*.gif"),
                ("BMP", "*.bmp"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.current_file = Path(file_path)
            self.file_label.config(text=str(self.current_file), foreground="black")
            
            # Display file size
            file_size = self.current_file.stat().st_size
            size_kb = file_size / 1024
            self.size_label.config(text=f"Size: {size_kb:.2f} KB")
            
            self._refresh_metadata()

    def _refresh_metadata(self):
        """Refresh metadata display for current file"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select an image file first")
            return

        # Run in separate thread to avoid freezing GUI
        self.operation_thread = threading.Thread(target=self._refresh_metadata_thread)
        self.operation_thread.start()

    def _refresh_metadata_thread(self):
        """Background thread for metadata extraction"""
        try:
            self._update_status("Loading metadata...", 25)
            
            # Parse metadata
            self.metadata_parser = MetadataParser(self.current_file)
            self.current_metadata = self.metadata_parser.extract_all()

            self._update_status("Displaying information...", 50)
            # Display information
            self._display_info()
            
            self._update_status("Displaying metadata...", 75)
            self._display_metadata()
            
            self._update_status(f"✅ Metadata loaded for {self.current_file.name}", 100)

        except Exception as e:
            self._update_status(f"❌ Error loading metadata: {e}", 0)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load metadata: {e}"))

    def _display_info(self):
        """Display basic file information"""
        if not self.current_metadata:
            return

        info = self.current_metadata.get('basic', {})
        
        text_content = "=== FILE INFORMATION ===\n\n"
        for key, value in info.items():
            text_content += f"{key:.<35} {value}\n"

        self.root.after(0, lambda: self._update_info_text(text_content))

    def _update_info_text(self, content: str):
        """Thread-safe info text update"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, content)
        self.info_text.config(state=tk.DISABLED)

    def _display_metadata(self):
        """Display detailed metadata in tabs"""
        if not self.current_metadata:
            return

        # EXIF tab
        exif_data = self.current_metadata.get('exif', {})
        exif_content = "=== EXIF DATA ===\n\n"
        if exif_data and any(exif_data.values()):
            for ifd_name, ifd_data in exif_data.items():
                if ifd_data:
                    exif_content += f"\n[{ifd_name}]\n"
                    exif_content += "-" * 60 + "\n"
                    for tag_name, value in ifd_data.items():
                        value_str = str(value)[:70]
                        exif_content += f"  {tag_name:.<30} {value_str}\n"
        else:
            exif_content += "No EXIF data found"

        # IPTC tab
        iptc_data = self.current_metadata.get('iptc', {})
        iptc_content = "=== IPTC DATA ===\n\n"
        if iptc_data:
            for key, value in iptc_data.items():
                value_str = str(value)[:70]
                iptc_content += f"{key:.<30} {value_str}\n"
        else:
            iptc_content += "No IPTC data found"

        # Other tab
        other_data = self.current_metadata.get('other', {})
        other_content = "=== OTHER METADATA ===\n\n"
        if other_data:
            for key, value in other_data.items():
                value_str = str(value)[:70]
                other_content += f"{key:.<30} {value_str}\n"
        else:
            other_content += "No other metadata found"

        # Update tabs in main thread
        self.root.after(0, lambda: self._update_exif_tab(exif_content))
        self.root.after(0, lambda: self._update_iptc_tab(iptc_content))
        self.root.after(0, lambda: self._update_other_tab(other_content))

    def _update_exif_tab(self, content: str):
        """Thread-safe EXIF tab update"""
        self.tabs['EXIF'].config(state=tk.NORMAL)
        self.tabs['EXIF'].delete(1.0, tk.END)
        self.tabs['EXIF'].insert(1.0, content)
        self.tabs['EXIF'].config(state=tk.DISABLED)

    def _update_iptc_tab(self, content: str):
        """Thread-safe IPTC tab update"""
        self.tabs['IPTC'].config(state=tk.NORMAL)
        self.tabs['IPTC'].delete(1.0, tk.END)
        self.tabs['IPTC'].insert(1.0, content)
        self.tabs['IPTC'].config(state=tk.DISABLED)

    def _update_other_tab(self, content: str):
        """Thread-safe Other tab update"""
        self.tabs['Other'].config(state=tk.NORMAL)
        self.tabs['Other'].delete(1.0, tk.END)
        self.tabs['Other'].insert(1.0, content)
        self.tabs['Other'].config(state=tk.DISABLED)

    def _analyze_file(self):
        """Analyze file and show summary"""
        if not self.current_file or not self.current_metadata:
            messagebox.showwarning("No Data", "Please load a file first")
            return

        analysis = self._generate_analysis()
        messagebox.showinfo("File Analysis", analysis)

    def _generate_analysis(self) -> str:
        """Generate analysis summary"""
        if not self.current_metadata:
            return "No metadata available"

        basic = self.current_metadata.get('basic', {})
        exif = self.current_metadata.get('exif', {})
        iptc = self.current_metadata.get('iptc', {})

        # Count metadata
        exif_count = sum(len(v) for v in exif.values() if v)
        iptc_count = len(iptc)

        analysis = f"""
📊 FILE ANALYSIS REPORT
{'=' * 50}

📋 BASIC INFORMATION
  File: {self.current_file.name}
  Format: {basic.get('Format', 'Unknown')}
  Size: {basic.get('File Size', 'Unknown')}
  Dimensions: {basic.get('Dimensions', 'Unknown')}
  Color Mode: {basic.get('Color Mode', 'Unknown')}

📸 METADATA SUMMARY
  EXIF Tags: {exif_count}
  IPTC Data: {iptc_count}
  Has EXIF: {'✅ Yes' if exif_count > 0 else '❌ No'}
  Has IPTC: {'✅ Yes' if iptc_count > 0 else '❌ No'}

🔍 PRIVACY ASSESSMENT
  Risk Level: {'⚠️  High' if exif_count > 0 else '✅ Low'}
  Sensitive Info: {'📍 GPS data found' if any('GPS' in str(v) for v in exif.values()) else 'No GPS data'}
"""
        return analysis

    def _strip_exif(self):
        """Strip EXIF data from current file"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select an image file first")
            return

        if messagebox.askyesno("Confirm", f"Remove EXIF data from {self.current_file.name}?\nA backup will be created."):
            self.operation_thread = threading.Thread(target=self._strip_exif_thread)
            self.operation_thread.start()

    def _strip_exif_thread(self):
        """Background thread for EXIF stripping"""
        try:
            self._update_status("Stripping EXIF data...", 50)

            modifier = MetadataModifier(self.current_file, create_backup=True)
            if modifier.remove_exif():
                self._update_status("✅ EXIF data removed", 100)
                self.root.after(0, lambda: messagebox.showinfo("Success", "EXIF data removed successfully"))
                self.root.after(0, self._refresh_metadata)
            else:
                self._update_status("❌ Failed to remove EXIF data", 0)
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to remove EXIF data"))

        except Exception as e:
            self._update_status(f"❌ Error: {e}", 0)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {e}"))

    def _strip_all(self):
        """Strip all metadata from current file"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select an image file first")
            return

        if messagebox.askyesno("Confirm", f"Remove ALL metadata from {self.current_file.name}?\nA backup will be created."):
            self.operation_thread = threading.Thread(target=self._strip_all_thread)
            self.operation_thread.start()

    def _strip_all_thread(self):
        """Background thread for stripping all metadata"""
        try:
            self._update_status("Stripping all metadata...", 50)

            modifier = MetadataModifier(self.current_file, create_backup=True)
            if modifier.strip_all_metadata():
                self._update_status("✅ All metadata removed", 100)
                self.root.after(0, lambda: messagebox.showinfo("Success", "All metadata removed successfully"))
                self.root.after(0, self._refresh_metadata)
            else:
                self._update_status("❌ Failed to strip metadata", 0)
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to strip metadata"))

        except Exception as e:
            self._update_status(f"❌ Error: {e}", 0)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {e}"))

    def _add_comment_dialog(self):
        """Show dialog to add comment"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select an image file first")
            return

        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Comment")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Enter comment text:", font=('Arial', 10)).pack(pady=10)

        text_area = tk.Text(dialog, height=6, wrap=tk.WORD, font=('Arial', 9))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def add_comment():
            comment = text_area.get(1.0, tk.END).strip()
            if not comment:
                messagebox.showwarning("Empty", "Please enter a comment")
                return

            self.operation_thread = threading.Thread(target=self._add_comment_thread, args=(comment,))
            self.operation_thread.start()
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="✅ Add", command=add_comment).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _add_comment_thread(self, comment: str):
        """Background thread for adding comment"""
        try:
            self._update_status("Adding comment...", 50)

            modifier = MetadataModifier(self.current_file, create_backup=True)
            if modifier.add_comment(comment):
                self._update_status("✅ Comment added", 100)
                self.root.after(0, lambda: messagebox.showinfo("Success", "Comment added successfully"))
                self.root.after(0, self._refresh_metadata)
            else:
                self._update_status("❌ Failed to add comment", 0)
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to add comment"))

        except Exception as e:
            self._update_status(f"❌ Error: {e}", 0)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {e}"))

    def _restore_backup(self):
        """Restore file from backup"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select an image file first")
            return

        backup_name = f"{self.current_file.stem}_backup{self.current_file.suffix}"
        backup_path = self.current_file.parent / backup_name

        if not backup_path.exists():
            messagebox.showwarning("No Backup", "No backup file found for this image")
            return

        if messagebox.askyesno("Confirm", "Restore original file from backup?"):
            self.operation_thread = threading.Thread(target=self._restore_backup_thread)
            self.operation_thread.start()

    def _restore_backup_thread(self):
        """Background thread for backup restoration"""
        try:
            self._update_status("Restoring from backup...", 50)

            modifier = MetadataModifier(self.current_file, create_backup=False)
            if modifier.restore_backup():
                self._update_status("✅ File restored", 100)
                self.root.after(0, lambda: messagebox.showinfo("Success", "File restored successfully"))
                self.root.after(0, self._refresh_metadata)
            else:
                self._update_status("❌ Failed to restore file", 0)
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to restore file"))

        except Exception as e:
            self._update_status(f"❌ Error: {e}", 0)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {e}"))

    def _export_json(self):
        """Export metadata as JSON"""
        if not self.current_metadata:
            messagebox.showwarning("No Data", "Please load metadata first")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self._update_status("Exporting JSON...", 50)
                
                # Write JSON manually (better control)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'file': str(self.current_file),
                        'metadata': self.current_metadata
                    }, f, indent=2, ensure_ascii=False)
                
                self._update_status(f"✅ Exported to {Path(file_path).name}", 100)
                messagebox.showinfo("Success", f"Metadata exported to {Path(file_path).name}")

            except Exception as e:
                self._update_status(f"❌ Export failed: {e}", 0)
                messagebox.showerror("Error", f"Export failed: {e}")

    def _export_csv(self):
        """Export metadata as CSV"""
        if not self.current_metadata:
            messagebox.showwarning("No Data", "Please load metadata first")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self._update_status("Exporting CSV...", 50)

                # Flatten metadata for CSV
                rows = []
                
                # Basic info
                for key, value in self.current_metadata.get('basic', {}).items():
                    rows.append({'Category': 'Basic', 'Key': key, 'Value': str(value)})
                
                # EXIF data
                for ifd_name, ifd_data in self.current_metadata.get('exif', {}).items():
                    if ifd_data:
                        for key, value in ifd_data.items():
                            rows.append({'Category': f'EXIF ({ifd_name})', 'Key': key, 'Value': str(value)})
                
                # IPTC data
                for key, value in self.current_metadata.get('iptc', {}).items():
                    rows.append({'Category': 'IPTC', 'Key': key, 'Value': str(value)})
                
                # Other data
                for key, value in self.current_metadata.get('other', {}).items():
                    rows.append({'Category': 'Other', 'Key': key, 'Value': str(value)})

                # Write CSV
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['Category', 'Key', 'Value'])
                    writer.writeheader()
                    writer.writerows(rows)

                self._update_status(f"✅ Exported to {Path(file_path).name}", 100)
                messagebox.showinfo("Success", f"Metadata exported to {Path(file_path).name}")

            except Exception as e:
                self._update_status(f"❌ Export failed: {e}", 0)
                messagebox.showerror("Error", f"Export failed: {e}")

    def _update_status(self, message: str, progress: int = 0):
        """Update status bar and progress bar"""
        def update():
            self.status_label.config(text=message)
            self.progress_var.set(progress)
            if progress >= 100:
                self.root.after(1000, lambda: self.progress_var.set(0))
        
        self.root.after(0, update)


def main():
    """Launch Scorpion GUI"""
    root = tk.Tk()
    gui = ScorpionGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
