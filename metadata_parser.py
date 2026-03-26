#!/usr/bin/env python3
"""
Metadata Parser - Extract EXIF and IPTC data from images
Handles multiple image formats and metadata standards
"""

from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import os


class MetadataParser:
    """Parse EXIF, IPTC, and basic metadata from images"""

    def __init__(self, file_path: Path):
        """
        Initialize metadata parser for a specific image.

        Args:
            file_path (Path): Path to image file
        """
        self.file_path = file_path
        self.image = None
        self.metadata = {
            'basic': {},
            'exif': {},
            'iptc': {},
            'other': {}
        }

    def extract_basic_metadata(self) -> Dict[str, Any]:
        """
        Extract basic image attributes (size, format, mode, etc).

        Returns:
            Dict: Basic metadata information
        """
        try:
            self.image = Image.open(self.file_path)

            basic = {
                'Filename': self.file_path.name,
                'File Path': str(self.file_path),
                'File Size': self._format_file_size(self.file_path.stat().st_size),
                'Format': self.image.format,
                'Dimensions': f"{self.image.width} x {self.image.height} pixels",
                'Color Mode': self.image.mode,
                'DPI': self.image.info.get('dpi', 'N/A')
            }

            self.metadata['basic'] = basic
            return basic

        except Exception as e:
            print(f"   ⚠️  Error extracting basic metadata: {e}")
            return {}

    def extract_exif_data(self) -> Dict[str, Any]:
        """
        Extract EXIF data from image using piexif.

        Returns:
            Dict: EXIF metadata organized by IFD
        """
        try:
            exif_dict = piexif.load(str(self.file_path))
            exif_data = {}

            # Process each IFD (Image File Directory)
            for ifd_name in ("0th", "Exif", "GPS", "1st"):
                ifd = exif_dict.get(ifd_name, {})
                exif_data[ifd_name] = {}

                for tag, value in ifd.items():
                    tag_name = piexif.TAGS[ifd_name][tag]["name"]
                    
                    # Format value appropriately
                    formatted_value = self._format_exif_value(value, ifd_name, tag)
                    exif_data[ifd_name][tag_name] = formatted_value

            self.metadata['exif'] = exif_data
            return exif_data

        except Exception as e:
            # Not all images have EXIF data
            print(f"   ⚠️  No EXIF data found or error reading: {e}")
            return {}

    def extract_iptc_data(self) -> Dict[str, Any]:
        """
        Extract IPTC metadata from image.

        Returns:
            Dict: IPTC metadata
        """
        try:
            # Try using PIL's info dict for IPTC data
            if self.image is None:
                self.image = Image.open(self.file_path)

            iptc_data = {}

            # PIL stores IPTC in the info dictionary
            if 'iptc' in self.image.info:
                # Parse raw IPTC data
                iptc_raw = self.image.info['iptc']
                iptc_data['Raw IPTC Data'] = str(iptc_raw)

            # Try to extract common IPTC fields from image info
            iptc_fields = {
                'description': 'Description',
                'keywords': 'Keywords',
                'copyright': 'Copyright',
                'creator': 'Creator',
                'title': 'Title'
            }

            for info_key, display_name in iptc_fields.items():
                if info_key in self.image.info:
                    iptc_data[display_name] = self.image.info[info_key]

            # Also check image description
            if self.image.info.get('description'):
                iptc_data['Description'] = self.image.info.get('description')

            self.metadata['iptc'] = iptc_data
            return iptc_data

        except Exception as e:
            print(f"   ⚠️  Error extracting IPTC data: {e}")
            return {}

    def extract_other_metadata(self) -> Dict[str, Any]:
        """
        Extract other metadata from image info dictionary.

        Returns:
            Dict: Additional metadata
        """
        try:
            if self.image is None:
                self.image = Image.open(self.file_path)

            other = {}
            
            # Exclude common keys we've already processed
            exclude_keys = {'dpi', 'iptc', 'exif', 'description', 
                          'keywords', 'copyright', 'creator', 'title'}

            for key, value in self.image.info.items():
                if key.lower() not in exclude_keys:
                    # Try to make value readable
                    if isinstance(value, bytes):
                        try:
                            other[key] = value.decode('utf-8', errors='ignore')
                        except:
                            other[key] = str(value)
                    else:
                        other[key] = str(value)

            self.metadata['other'] = other
            return other

        except Exception as e:
            print(f"   ⚠️  Error extracting other metadata: {e}")
            return {}

    def extract_all(self) -> Dict[str, Any]:
        """
        Extract all available metadata from image.

        Returns:
            Dict: Complete metadata dictionary
        """
        self.extract_basic_metadata()
        self.extract_exif_data()
        self.extract_iptc_data()
        self.extract_other_metadata()
        return self.metadata

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get extracted metadata.

        Returns:
            Dict: Metadata dictionary
        """
        return self.metadata

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size_bytes (int): File size in bytes

        Returns:
            str: Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    @staticmethod
    def _format_exif_value(value: Any, ifd_name: str, tag: int) -> str:
        """
        Format EXIF value for display.

        Args:
            value: EXIF value
            ifd_name (str): IFD name (0th, Exif, GPS, 1st)
            tag (int): Tag number

        Returns:
            str: Formatted value
        """
        try:
            # Handle GPS coordinates
            if ifd_name == "GPS":
                if isinstance(value, bytes):
                    return value.decode('utf-8', errors='ignore')
                return str(value)

            # Handle bytes
            if isinstance(value, bytes):
                try:
                    return value.decode('utf-8', errors='ignore')
                except:
                    return str(value)

            # Handle tuples (common in EXIF)
            if isinstance(value, tuple):
                return str(value)

            return str(value)

        except Exception as e:
            return f"<Error parsing value: {e}>"
