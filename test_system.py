import os
import sys
from forensics_detective import SimpleDetective

def run_tests():
    """Main testing function for the digital forensics system"""

    # Initialize the expert system
    detective = SimpleDetective()

    # Register original images
    originals_folder = "originals"
    if os.path.exists(originals_folder):
        detective.register_targets(originals_folder)
    else:
        print(f"[ERROR] Originals folder '{originals_folder}' not found")
        return

    # Test folders
    test_folders = ["modified_images", "random"]

    results = {
        "total_processed": 0,
        "matches_found": 0,
        "correct_rejections": 0,
        "false_positives": 0,
        "false_negatives": 0
    }

    # Process all test images
    for folder in test_folders:
        if not os.path.exists(folder):
            print(f"[WARNING] Test folder '{folder}' not found")
            continue

        print(f"\n{'='*60}")
        print(f"Processing folder: {folder}")
        print(f"{'='*60}")

        for filename in sorted(os.listdir(folder)):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(folder, filename)

                print(f"\nProcessing: {filename}")

                # Find best match
                best_match, score, evidence = detective.find_best_match(filepath)

                # Display rule reasoning
                meta_score, meta_evidence = evidence.get('metadata', (0, []))
                hash_score, hash_evidence = evidence.get('image_hash', (0, []))
                template_score, template_evidence = evidence.get('template', (0, []))

                # Format evidence strings
                meta_status = "FIRED" if meta_score > 0 else "NO MATCH"
                hash_status = "FIRED" if hash_score > 0 else "NO MATCH"  
                template_status = "FIRED" if template_score > 0 else "NO MATCH"

                print(f"Rule 1 (Metadata): {meta_status} - {', '.join(meta_evidence)} -> {meta_score}/30 points")
                print(f"Rule 2 (Image Hash): {hash_status} - {', '.join(hash_evidence)} -> {hash_score}/10 points")
                print(f"Rule 3 (Template): {template_status} - {', '.join(template_evidence)} -> {template_score}/60 points")

                # Final decision
                if best_match:
                    print(f"Final Score: {score}/100 -> MATCH to {best_match}")
                    results["matches_found"] += 1
                else:
                    print(f"Final Score: {score}/100 -> REJECTED")
                    if folder == "random":
                        results["correct_rejections"] += 1

                results["total_processed"] += 1

    # Print summary statistics
    print(f"\n{'='*60}")
    print("SUMMARY STATISTICS")
    print(f"{'='*60}")
    print(f"Total images processed: {results['total_processed']}")
    print(f"Matches found: {results['matches_found']}")
    print(f"Correct rejections: {results['correct_rejections']}")

    # Calculate accuracy
    if results['total_processed'] > 0:
        match_rate = (results['matches_found'] / results['total_processed']) * 100
        print(f"Overall match rate: {match_rate:.1f}%")

    print("\n[INFO] Testing complete!")

if __name__ == "__main__":
    run_tests()