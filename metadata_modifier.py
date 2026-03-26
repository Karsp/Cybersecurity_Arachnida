#!/usr/bin/env python3
"""
Metadata Modifier - Modify, delete, and clean metadata from images
Supports EXIF, IPTC, and other metadata manipulation
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image
import piexif
import shutil
from datetime import datetime


class MetadataModifier:
    """Modify and clean metadata from images"""

    VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

    def __init__(self, file_path: Path, create_backup: bool = True):
        """
        Initialize metadata modifier for a specific image.

        Args:
            file_path (Path): Path to image file
            create_backup (bool): Whether to create backup before modification
        """
        self.file_path = file_path
        self.create_backup = create_backup
        self.backup_path = None
        self.modified = False

    def create_backup_file(self) -> bool:
        """
        Create a backup copy of the original file.

        Returns:
            bool: True if backup created successfully
        """
        try:
            if not self.create_backup:
                return True

            backup_name = f"{self.file_path.stem}_backup{self.file_path.suffix}"
            self.backup_path = self.file_path.parent / backup_name

            # Don't overwrite existing backups
            counter = 1
            while self.backup_path.exists():
                backup_name = f"{self.file_path.stem}_backup_{counter}{self.file_path.suffix}"
                self.backup_path = self.file_path.parent / backup_name
                counter += 1

            shutil.copy2(self.file_path, self.backup_path)
            return True

        except Exception as e:
            print(f"   ⚠️  Could not create backup: {e}")
            return False

    def remove_exif(self) -> bool:
        """
        Remove all EXIF data from JPEG image.

        Returns:
            bool: True if successful
        """
        try:
            if self.file_path.suffix.lower() not in ['.jpg', '.jpeg']:
                print(f"   ⚠️  EXIF removal only supported for JPEG files")
                return False

            # Create backup if needed
            if not self.create_backup_file():
                return False

            # Open image and remove EXIF
            image = Image.open(self.file_path)
            
            # Create new image without EXIF
            data = list(image.getdata())
            image_without_exif = Image.new(image.mode, image.size)
            image_without_exif.putdata(data)

            # Save without EXIF
            image_without_exif.save(self.file_path, quality=95)
            self.modified = True
            return True

        except Exception as e:
            print(f"   ❌ Error removing EXIF: {e}")
            return False

    def remove_specific_exif_tags(self, tags: List[str]) -> bool:
        """
        Remove specific EXIF tags from image.

        Args:
            tags (List[str]): List of EXIF tag names to remove

        Returns:
            bool: True if successful
        """
        try:
            if self.file_path.suffix.lower() not in ['.jpg', '.jpeg']:
                print(f"   ⚠️  EXIF operations only supported for JPEG files")
                return False

            # Create backup if needed
            if not self.create_backup_file():
                return False

            # Load EXIF data
            exif_dict = piexif.load(str(self.file_path))
            removed_count = 0

            # Find and remove specified tags
            for ifd_name in ("0th", "Exif", "GPS", "1st"):
                ifd = exif_dict.get(ifd_name, {})
                tags_to_remove = []

                for tag, value in ifd.items():
                    tag_name = piexif.TAGS[ifd_name][tag]["name"]
                    if tag_name in tags:
                        tags_to_remove.append(tag)
                        removed_count += 1

                # Remove tags
                for tag in tags_to_remove:
                    del ifd[tag]

            if removed_count == 0:
                print(f"   ⚠️  No matching tags found to remove")
                return False

            # Save modified EXIF
            exif_bytes = piexif.dump(exif_dict)
            image = Image.open(self.file_path)
            image.save(self.file_path, exif=exif_bytes, quality=95)
            
            self.modified = True
            print(f"   ✅ Removed {removed_count} EXIF tag(s)")
            return True

        except Exception as e:
            print(f"   ❌ Error removing specific EXIF tags: {e}")
            return False

    def set_exif_tag(self, tag_name: str, value: Any) -> bool:
        """
        Set or modify an EXIF tag value.

        Args:
            tag_name (str): EXIF tag name
            value: New value for the tag

        Returns:
            bool: True if successful
        """
        try:
            if self.file_path.suffix.lower() not in ['.jpg', '.jpeg']:
                print(f"   ⚠️  EXIF operations only supported for JPEG files")
                return False

            # Create backup if needed
            if not self.create_backup_file():
                return False

            # Load EXIF data
            exif_dict = piexif.load(str(self.file_path))
            tag_found = False

            # Find tag in IFDs
            for ifd_name in ("0th", "Exif", "GPS", "1st"):
                ifd = exif_dict.get(ifd_name, {})
                for tag, current_value in ifd.items():
                    if piexif.TAGS[ifd_name][tag]["name"] == tag_name:
                        ifd[tag] = self._format_exif_value(value, ifd_name)
                        tag_found = True
                        break

            if not tag_found:
                print(f"   ⚠️  Tag '{tag_name}' not found in image")
                return False

            # Save modified EXIF
            exif_bytes = piexif.dump(exif_dict)
            image = Image.open(self.file_path)
            image.save(self.file_path, exif=exif_bytes, quality=95)

            self.modified = True
            print(f"   ✅ Set '{tag_name}' to '{value}'")
            return True

        except Exception as e:
            print(f"   ❌ Error setting EXIF tag: {e}")
            return False

    def strip_all_metadata(self) -> bool:
        """
        Remove all metadata from image, keeping only image data.

        Returns:
            bool: True if successful
        """
        try:
            # Create backup if needed
            if not self.create_backup_file():
                return False

            # Open and reprocess image to remove all metadata
            image = Image.open(self.file_path)

            # Create new image with same content but no metadata
            data = list(image.getdata())
            image_clean = Image.new(image.mode, image.size)
            image_clean.putdata(data)

            # Save with minimal metadata
            if self.file_path.suffix.lower() in ['.jpg', '.jpeg']:
                image_clean.save(self.file_path, quality=95)
            else:
                image_clean.save(self.file_path)

            self.modified = True
            return True

        except Exception as e:
            print(f"   ❌ Error stripping metadata: {e}")
            return False

    def add_comment(self, comment: str) -> bool:
        """
        Add a comment to the image.

        Args:
            comment (str): Comment text

        Returns:
            bool: True if successful
        """
        try:
            # Create backup if needed
            if not self.create_backup_file():
                return False

            image = Image.open(self.file_path)
            image.info['comment'] = comment.encode('utf-8')
            image.save(self.file_path)

            self.modified = True
            return True

        except Exception as e:
            print(f"   ❌ Error adding comment: {e}")
            return False

    def restore_backup(self) -> bool:
        """
        Restore image from backup file.

        Returns:
            bool: True if successful
        """
        try:
            if not self.backup_path or not self.backup_path.exists():
                print(f"   ❌ No backup file found")
                return False

            shutil.copy2(self.backup_path, self.file_path)
            self.modified = False
            return True

        except Exception as e:
            print(f"   ❌ Error restoring backup: {e}")
            return False

    def get_modification_status(self) -> Dict[str, Any]:
        """
        Get modification status and details.

        Returns:
            Dict: Status information
        """
        return {
            'file_path': str(self.file_path),
            'modified': self.modified,
            'backup_path': str(self.backup_path) if self.backup_path else None,
            'file_size': self.file_path.stat().st_size
        }

    @staticmethod
    def _format_exif_value(value: Any, ifd_name: str) -> Any:
        """
        Format value for EXIF storage.

        Args:
            value: Value to format
            ifd_name (str): IFD name

        Returns:
            Formatted value for EXIF
        """
        if isinstance(value, str):
            return value.encode('utf-8')
        if isinstance(value, int):
            return (value, 1)  # Rational format
        return value
