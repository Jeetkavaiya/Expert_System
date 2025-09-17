import cv2
import imagehash
import numpy as np
from PIL import Image

def check_metadata(original_metadata, input_metadata):
    """
    Rule 1: Metadata Analysis - Compare file size and basic properties
    Returns: (score, evidence_list) where score is 0-30 points
    """
    score = 0
    evidence = []

    # File size comparison (up to 20 points)
    original_size = original_metadata.get('size', 0)
    input_size = input_metadata.get('size', 0)

    if original_size > 0 and input_size > 0:
        size_ratio = min(original_size, input_size) / max(original_size, input_size)
        if size_ratio > 0.8:
            score += 20
            evidence.append(f"Size ratio {size_ratio:.2f}")
        elif size_ratio > 0.6:
            score += 15
            evidence.append(f"Moderate size ratio {size_ratio:.2f}")
        elif size_ratio > 0.3:
            score += 8
            evidence.append(f"Low size ratio {size_ratio:.2f}")

    # Dimension comparison (up to 5 points)
    if ('width' in original_metadata and 'width' in input_metadata and
        'height' in original_metadata and 'height' in input_metadata):

        original_pixels = original_metadata['width'] * original_metadata['height']
        input_pixels = input_metadata['width'] * input_metadata['height']

        if original_pixels > 0 and input_pixels > 0:
            pixel_ratio = min(original_pixels, input_pixels) / max(original_pixels, input_pixels)
            score += int(pixel_ratio * 5)
            evidence.append(f"Dimension similarity {pixel_ratio:.2f}")

    # EXIF data comparison (up to 5 points)
    original_exif = original_metadata.get('exif', {})
    input_exif = input_metadata.get('exif', {})

    if original_exif and input_exif:
        matching_tags = 0
        total_tags = 0
        for tag in ['Make', 'Model', 'Software']:
            if tag in original_exif:
                total_tags += 1
                if tag in input_exif and original_exif[tag] == input_exif[tag]:
                    matching_tags += 1

        if total_tags > 0:
            exif_score = int((matching_tags / total_tags) * 5)
            score += exif_score
            evidence.append(f"EXIF matches {matching_tags}/{total_tags}")

    final_score = min(score, 30)  # Cap at 30 points

    if final_score >= 25:
        return final_score, ["METADATA_SIMILAR"] + evidence
    elif final_score > 0:
        return final_score, ["METADATA_PARTIAL"] + evidence
    else:
        return 0, ["METADATA_DIFFERENT"]

def check_hashes(original_hashes, input_hashes):
    """
    Rule 2: Image Hashing - Use perceptual hashes to detect visual similarity
    Returns: (score, evidence_list) where score is 0-10 points
    """
    if not original_hashes or not input_hashes:
        return 0, ["NO_HASH_DATA"]

    try:
        similarity_scores = []
        evidence_details = []

        # Test multiple hash types
        hash_types = ['phash', 'ahash', 'dhash', 'whash']

        for hash_type in hash_types:
            if hash_type in original_hashes and hash_type in input_hashes:
                # Convert hex strings to hash objects
                original_hash = imagehash.hex_to_hash(original_hashes[hash_type])
                input_hash = imagehash.hex_to_hash(input_hashes[hash_type])

                # Calculate Hamming distance
                hamming_distance = original_hash - input_hash

                # Convert distance to similarity percentage
                max_distance = 64
                similarity = max(0, (max_distance - hamming_distance) / max_distance * 100)

                similarity_scores.append(similarity)
                evidence_details.append(f"{hash_type}: {similarity:.1f}% (distance: {hamming_distance})")

        if not similarity_scores:
            return 0, ["NO_VALID_HASHES"]

        # Use the best similarity score
        best_similarity = max(similarity_scores)

        # Convert similarity percentage to points (0-10)
        if best_similarity >= 90:
            score = 10
            status = "EXCELLENT_MATCH"
        elif best_similarity >= 80:
            score = 8
            status = "GOOD_MATCH"
        elif best_similarity >= 70:
            score = 6
            status = "MODERATE_MATCH"
        elif best_similarity >= 50:
            score = 4
            status = "WEAK_MATCH"
        elif best_similarity >= 30:
            score = 2
            status = "POOR_MATCH"
        else:
            score = 0
            status = "NO_MATCH"

        evidence = [f"{status} - Best: {best_similarity:.1f}%"] + evidence_details
        return score, evidence

    except Exception as e:
        return 0, [f"IMAGE_HASH_ERROR: {str(e)}"]

def check_template(original_image, input_image):
    """
    Rule 3: Template Matching - Use OpenCV to detect visual similarity
    Returns: (score, evidence_list) where score is 0-60 points
    """
    if original_image is None or input_image is None:
        return 0, ["NO_IMAGE_DATA"]

    try:
        # Convert to grayscale
        if len(original_image.shape) == 3:
            original_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        else:
            original_gray = original_image.copy()

        if len(input_image.shape) == 3:
            input_gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
        else:
            input_gray = input_image.copy()

        # Get image dimensions
        orig_h, orig_w = original_gray.shape
        input_h, input_w = input_gray.shape

        max_correlation = 0
        evidence = []

        # Case 1: Input might be a crop of original
        if input_h <= orig_h and input_w <= orig_w:
            result = cv2.matchTemplate(original_gray, input_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            max_correlation = max(max_correlation, max_val)
            evidence.append(f"Input-in-Original: {max_val:.3f}")

        # Case 2: Original might be a crop of input
        if orig_h <= input_h and orig_w <= input_w:
            result = cv2.matchTemplate(input_gray, original_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            max_correlation = max(max_correlation, max_val)
            evidence.append(f"Original-in-Input: {max_val:.3f}")

        # Case 3: Multi-scale template matching
        if abs(orig_h - input_h) > 100 or abs(orig_w - input_w) > 100:
            scales = [0.5, 0.75, 1.0, 1.25, 1.5]
            for scale in scales:
                if scale != 1.0:
                    new_w, new_h = int(input_w * scale), int(input_h * scale)
                    if new_w > 0 and new_h > 0 and new_w <= orig_w and new_h <= orig_h:
                        resized = cv2.resize(input_gray, (new_w, new_h))
                        result = cv2.matchTemplate(original_gray, resized, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, _ = cv2.minMaxLoc(result)
                        max_correlation = max(max_correlation, max_val)
                        evidence.append(f"Scale {scale}: {max_val:.3f}")

        # Convert correlation to score (0-60 points)
        score = int(max_correlation * 60)

        # Add match quality description
        if max_correlation >= 0.9:
            evidence.insert(0, "EXCELLENT_MATCH")
        elif max_correlation >= 0.8:
            evidence.insert(0, "GOOD_MATCH")
        elif max_correlation >= 0.6:
            evidence.insert(0, "MODERATE_MATCH")
        elif max_correlation >= 0.3:
            evidence.insert(0, "WEAK_MATCH")
        else:
            evidence.insert(0, "NO_MATCH")

        return score, evidence

    except Exception as e:
        return 0, [f"TEMPLATE_MATCHING_ERROR: {str(e)}"]

# Keep original function names for backward compatibility
def apply_metadata_rule(original_metadata, input_metadata):
    return check_metadata(original_metadata, input_metadata)

def apply_image_hash_rule(original_hashes, input_hashes):
    return check_hashes(original_hashes, input_hashes)

def apply_template_matching_rule(original_image, input_image):
    return check_template(original_image, input_image)

# Helper functions
def compare_perceptual_hashes(hash1_str, hash2_str):
    """Compare two perceptual hash strings"""
    try:
        hash1 = imagehash.hex_to_hash(hash1_str)
        hash2 = imagehash.hex_to_hash(hash2_str)

        hamming_distance = hash1 - hash2
        max_distance = 64
        similarity = max(0, (max_distance - hamming_distance) / max_distance * 100)

        return similarity, hamming_distance
    except:
        return 0, 64

def get_best_hash_match(original_hashes, input_hashes):
    """Find the best matching hash type"""
    best_similarity = 0
    best_type = None

    for hash_type in ['phash', 'ahash', 'dhash', 'whash']:
        if hash_type in original_hashes and hash_type in input_hashes:
            similarity, _ = compare_perceptual_hashes(
                original_hashes[hash_type], 
                input_hashes[hash_type]
            )
            if similarity > best_similarity:
                best_similarity = similarity
                best_type = hash_type

    return best_similarity, best_type