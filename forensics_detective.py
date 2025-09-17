import os
import numpy as np
from PIL import Image, ExifTags
import cv2
import imagehash
from datetime import datetime


class SimpleDetective:
    def __init__(self):
        self.targets = {}

    def register_targets(self, folder):
        """Load and compute signatures for originals"""
        print(f"[INFO] Registering targets from folder: {folder}")

        if not os.path.exists(folder):
            raise ValueError(f"Folder {folder} does not exist")

        for filename in os.listdir(folder):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                filepath = os.path.join(folder, filename)
                try:
                    # Extract metadata
                    metadata = self._get_metadata(filepath)

                    # Compute image hashes
                    image_hashes = self._get_hashes(filepath)

                    # Load image for template matching
                    image = cv2.imread(filepath)

                    # Store all signatures
                    self.targets[filename] = {
                        "path": filepath,
                        "metadata": metadata,
                        "image_hashes": image_hashes,
                        "image": image,
                    }
                    print(f"[INFO] Registered {filename}")

                except Exception as e:
                    print(f"[WARNING] Failed to register {filename}: {e}")

        print(f"[INFO] Successfully registered {len(self.targets)} target images")

    def find_best_match(self, input_image_path):
        """Compare input to all targets using rules"""
        if not os.path.exists(input_image_path):
            raise ValueError(f"Input image {input_image_path} does not exist")

        try:
            # Extract input image signatures
            input_metadata = self._get_metadata(input_image_path)
            input_image_hashes = self._get_hashes(input_image_path)
            input_image = cv2.imread(input_image_path)

        except Exception as e:
            print(f"[ERROR] Failed to process input image: {e}")
            return None, 0, {}

        best_match = None
        best_score = 0
        best_evidence = {}

        # Compare against all targets
        for target_name, target_data in self.targets.items():

            # Apply Rule 1: Metadata Analysis
            from rules import check_metadata

            meta_score, meta_evidence = check_metadata(
                target_data["metadata"], input_metadata
            )

            # Apply Rule 2: Image Hashing
            from rules import check_hashes

            hash_score, hash_evidence = check_hashes(
                target_data["image_hashes"], input_image_hashes
            )

            # Apply Rule 3: Template Matching
            from rules import check_template

            template_score, template_evidence = check_template(
                target_data["image"], input_image
            )

            # Calculate total score
            total_score = meta_score + hash_score + template_score

            # Track best match
            if total_score > best_score:
                best_score = total_score
                best_match = target_name
                best_evidence = {
                    "metadata": (meta_score, meta_evidence),
                    "image_hash": (hash_score, hash_evidence),
                    "template": (template_score, template_evidence),
                }

        # Return best match if above threshold
        if best_score >= 60:
            return best_match, best_score, best_evidence
        else:
            return None, best_score, best_evidence

    def _get_metadata(self, image_path):
        """Extract metadata from an image"""
        metadata = {}
        try:
            # Get file stats
            stat = os.stat(image_path)
            metadata["size"] = stat.st_size
            metadata["modified"] = stat.st_mtime

            # Open image and get basic properties
            with Image.open(image_path) as img:
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["format"] = img.format
                metadata["mode"] = img.mode

                # Extract EXIF data
                exif_data = {}
                exif = img.getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                metadata["exif"] = exif_data

        except Exception as e:
            print(f"[WARNING] Error extracting metadata from {image_path}: {e}")

        return metadata

    def _get_hashes(self, image_path):
        """Compute perceptual hashes for image"""
        hashes = {}

        try:
            with Image.open(image_path) as img:
                hashes["ahash"] = str(imagehash.average_hash(img))
                hashes["phash"] = str(imagehash.phash(img))
                hashes["dhash"] = str(imagehash.dhash(img))
                hashes["whash"] = str(imagehash.whash(img))

        except Exception as e:
            print(f"[WARNING] Error computing hashes for {image_path}: {e}")

        return hashes
