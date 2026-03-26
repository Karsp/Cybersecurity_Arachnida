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
import threading


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
        self.root.title("Scorpion - Image Metadata Manager")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        self.current_file = None
        self.current_metadata = None
        self.metadata_parser = None
        
        self._create_widgets()
        self._setup_styles()

    def _setup_styles(self):
        """Configure ttk styles for better appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define colors
        style.configure('TFrame', background='#f0f0f0')
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'), background='#f0f0f0')
        style.configure('TButton', font=('Arial', 9))

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
        left_frame = ttk.LabelFrame(main_frame, text="File & Actions", padding="10")
        left_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)

        # File selection button
        btn_select = ttk.Button(left_frame, text="📁 Open Image", command=self._select_file)
        btn_select.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        # Current file label
        ttk.Label(left_frame, text="Current File:", font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.file_label = ttk.Label(left_frame, text="None selected", foreground="gray", wraplength=200, justify=tk.LEFT)
        self.file_label.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # ========== EXTRACTION SECTION ==========
        ttk.Separator(left_frame, orient='horizontal').grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(left_frame, text="Extraction", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(5, 10))
        
        btn_refresh = ttk.Button(left_frame, text="🔍 Refresh Metadata", command=self._refresh_metadata)
        btn_refresh.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)

        # ========== MODIFICATION SECTION ==========
        ttk.Separator(left_frame, orient='horizontal').grid(row=6, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(left_frame, text="Modifications", font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky=tk.W, pady=(5, 10))

        btn_strip_exif = ttk.Button(left_frame, text="❌ Strip EXIF", command=self._strip_exif)
        btn_strip_exif.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=5)

        btn_strip_all = ttk.Button(left_frame, text="🗑️  Strip All Metadata", command=self._strip_all)
        btn_strip_all.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=5)

        btn_add_comment = ttk.Button(left_frame, text="📝 Add Comment", command=self._add_comment_dialog)
        btn_add_comment.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=5)

        btn_restore = ttk.Button(left_frame, text="↩️  Restore from Backup", command=self._restore_backup)
        btn_restore.grid(row=11, column=0, sticky=(tk.W, tk.E), pady=5)

        # ========== UTILITY SECTION ==========
        ttk.Separator(left_frame, orient='horizontal').grid(row=12, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(left_frame, text="Utilities", font=('Arial', 10, 'bold')).grid(row=13, column=0, sticky=tk.W, pady=(5, 10))

        btn_export_json = ttk.Button(left_frame, text="📤 Export as JSON", command=self._export_json)
        btn_export_json.grid(row=14, column=0, sticky=(tk.W, tk.E), pady=5)

        btn_export_csv = ttk.Button(left_frame, text="📊 Export as CSV", command=self._export_csv)
        btn_export_csv.grid(row=15, column=0, sticky=(tk.W, tk.E), pady=5)

        # ========== TOP RIGHT PANEL: File Info ==========
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding="10")
        info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)

        # Basic info display
        self.info_text = scrolledtext.ScrolledText(info_frame, height=12, wrap=tk.WORD, font=('Courier', 9))
        self.info_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.info_text.config(state=tk.DISABLED)

        # ========== BOTTOM RIGHT PANEL: Detailed Metadata ==========
        detail_frame = ttk.LabelFrame(main_frame, text="Detailed Metadata", padding="10")
        detail_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(1, weight=1)

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
        
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT)

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
            self._refresh_metadata()

    def _refresh_metadata(self):
        """Refresh metadata display for current file"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select an image file first")
            return

        try:
            self._update_status("Loading metadata...")
            self.root.update()

            # Parse metadata
            self.metadata_parser = MetadataParser(self.current_file)
            self.current_metadata = self.metadata_parser.extract_all()

            # Display information
            self._display_info()
            self._display_metadata()
            self._update_status(f"✅ Metadata loaded for {self.current_file.name}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load metadata: {e}")
            self._update_status(f"❌ Error loading metadata")

    def _display_info(self):
        """Display basic file information"""
        if not self.current_metadata:
            return

        info = self.current_metadata.get('basic', {})
        
        text_content = "=== FILE INFORMATION ===\n\n"
        for key, value in info.items():
            text_content += f"{key:.<30} {value}\n"

        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text_content)
        self.info_text.config(state=tk.DISABLED)

    def _display_metadata(self):
        """Display detailed metadata in tabs"""
        if not self.current_metadata:
            return

        # EXIF tab
        exif_data = self.current_metadata.get('exif', {})
        exif_content = "=== EXIF DATA ===\n\n"
        for ifd_name, ifd_data in exif_data.items():
            if ifd_data:
                exif_content += f"\n[{ifd_name}]\n"
                for tag_name, value in ifd_data.items():
                    value_str = str(value)[:80]
                    exif_content += f"  {tag_name}: {value_str}\n"

        self.tabs['EXIF'].config(state=tk.NORMAL)
        self.tabs['EXIF'].delete(1.0, tk.END)
        self.tabs['EXIF'].insert(1.0, exif_content if exif_content.strip() != "=== EXIF DATA ===\n\n" else "No EXIF data found")
        self.tabs['EXIF'].config(state=tk.DISABLED)

        # IPTC tab
        iptc_data = self.current_metadata.get('iptc', {})
        iptc_content = "=== IPTC DATA ===\n\n"
        for key, value in iptc_data.items():
            value_str = str(value)[:80]
            iptc_content += f"{key}: {value_str}\n"

        self.tabs['IPTC'].config(state=tk.NORMAL)
        self.tabs['IPTC'].delete(1.0, tk.END)
        self.tabs['IPTC'].insert(1.0, iptc_content if iptc_content.strip() != "=== IPTC DATA ===\n\n" else "No IPTC data found")
        self.tabs['IPTC'].config(state=tk.DISABLED)

        # Other tab
        other_data = self.current_metadata.get('other', {})
        other_content = "=== OTHER METADATA ===\n\n"
        for key, value in other_data.items():
            value_str = str(value)[:80]
            other_content += f"{key}: {value_str}\n"

        self.tabs['Other'].config(state=tk.NORMAL)
        self.tabs['Other'].delete(1.0, tk.END)
        self.tabs['Other'].insert(1.0, other_content if other_content.strip() != "=== OTHER METADATA ===\n\n" else "No other metadata found")
        self.tabs['Other'].config(state=tk.DISABLED)

    def _strip_exif(self):
        """Strip EXIF data from current file"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select an image file first")
            return

        if messagebox.askyesno("Confirm", f"Remove EXIF data from {self.current_file.name}?\nA backup will be created."):
            try:
                self._update_status("Stripping EXIF data...")
                self.root.update()

                modifier = MetadataModifier(self.current_file, create_backup=True)
                if modifier.remove_exif():
                    messagebox.showinfo("Success", "EXIF data removed successfully")
                    self._refresh_metadata()
                else:
                    messagebox.showerror("Error", "Failed to remove EXIF data")

            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                self._update_status("Ready")

    def _strip_all(self):
        """Strip all metadata from current file"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select an image file first")
            return

        if messagebox.askyesno("Confirm", f"Remove ALL metadata from {self.current_file.name}?\nA backup will be created."):
            try:
                self._update_status("Stripping all metadata...")
                self.root.update()

                modifier = MetadataModifier(self.current_file, create_backup=True)
                if modifier.strip_all_metadata():
                    messagebox.showinfo("Success", "All metadata removed successfully")
                    self._refresh_metadata()
                else:
                    messagebox.showerror("Error", "Failed to strip metadata")

            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                self._update_status("Ready")

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

            try:
                self._update_status("Adding comment...")
                self.root.update()

                modifier = MetadataModifier(self.current_file, create_backup=True)
                if modifier.add_comment(comment):
                    messagebox.showinfo("Success", "Comment added successfully")
                    self._refresh_metadata()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to add comment")

            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                self._update_status("Ready")

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="✅ Add", command=add_comment).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

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
            try:
                self._update_status("Restoring from backup...")
                self.root.update()

                modifier = MetadataModifier(self.current_file, create_backup=False)
                if modifier.restore_backup():
                    messagebox.showinfo("Success", "File restored successfully")
                    self._refresh_metadata()
                else:
                    messagebox.showerror("Error", "Failed to restore file")

            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                self._update_status("Ready")

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
                import json
                from output_formatter import OutputFormatter

                formatter = OutputFormatter(output_format='json', output_file=file_path)
                formatter.add_result(str(self.current_file), self.current_metadata)
                formatter.save(file_path)
                messagebox.showinfo("Success", f"Metadata exported to {Path(file_path).name}")

            except Exception as e:
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
                from output_formatter import OutputFormatter

                formatter = OutputFormatter(output_format='csv', output_file=file_path)
                formatter.add_result(str(self.current_file), self.current_metadata)
                formatter.save(file_path)
                messagebox.showinfo("Success", f"Metadata exported to {Path(file_path).name}")

            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    def _update_status(self, message: str):
        """Update status bar"""
        self.status_label.config(text=message)


def main():
    """Launch Scorpion GUI"""
    root = tk.Tk()
    gui = ScorpionGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
