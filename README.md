# Digital Forensics Expert System

## Project Overview

This project implements a **digital forensics expert system** designed to match modified images back to their originals using a three-rule evidence-based approach. The system serves as a simplified version of real forensic image analysis tools, demonstrating classical AI expert system principles applied to digital evidence authentication.

### Objectives
- Build a rule-based expert system for image similarity detection
- Achieve ≥60% accuracy on modified images
- Maintain low false positive rates on random images
- Provide a transparent, explainable decision-making process

---

## System Architecture

The expert system implements a **three-tier analysis framework**:

```
Input Image → SimpleDetective → Rule Engine → Decision (Match/Reject)
                    ↓
            [Rule 1: Metadata Analysis]     (0-30 points)
            [Rule 2: Image Hashing]         (0-10 points)  
            [Rule 3: Template Matching]     (0-60 points)
                    ↓
            Total Score ≥ 60 → MATCH
            Total Score < 60 → REJECT
```

---

## Required Libraries and Dependencies

### Core Dependencies
```bash
pip install pillow imagehash opencv-python numpy
```

### Library Usage
- **PIL (Pillow)**: Image processing, metadata extraction, EXIF data reading
- **imagehash**: Perceptual hashing algorithms (pHash, aHash, dHash, wHash)
- **OpenCV (cv2)**: Template matching, image correlation, grayscale conversion
- **NumPy**: Array operations, mathematical computations
- **Standard Libraries**: `os`, `sys` for file operations

---

## Three-Rule Analysis System

### Rule 1: Metadata Analysis (0-30 points)
**Purpose**: Compare file properties and technical metadata

**Implementation Details**:
- **File Size Comparison** (up to 20 points):
  - Calculates size ratio: `min(size1, size2) / max(size1, size2)`
  - >80% similarity → 20 points
  - 60-80% similarity → 15 points  
  - 30-60% similarity → 8 points

- **Dimension Analysis** (up to 5 points):
  - Compares pixel count ratios
  - Accounts for cropping and scaling

- **EXIF Data Cross-reference** (up to 5 points):
  - Matches camera metadata (Make, Model, Software)
  - Weighted importance scoring

**Strengths**: Fast execution, effective for format conversions
**Weaknesses**: Vulnerable to metadata stripping

### Rule 2: Image Hashing (0-10 points)  
**Purpose**: Detect visual similarity using perceptual hashes

**Hash Algorithm Portfolio**:
- **pHash (Perceptual Hash)**: DCT-based, robust to minor changes
- **aHash (Average Hash)**: Simple averaging, fast computation
- **dHash (Difference Hash)**: Gradient-based, good for crops
- **wHash (Wavelet Hash)**: Frequency domain analysis

**Scoring System**:
- ≥90% similarity → 10 points (Excellent Match)
- 80-89% similarity → 8 points (Good Match)
- 70-79% similarity → 6 points (Moderate Match)
- 50-69% similarity → 4 points (Weak Match)
- 30-49% similarity → 2 points (Poor Match)
- <30% similarity → 0 points (No Match)

**Technical Implementation**:
```python
hamming_distance = original_hash - input_hash
similarity = max(0, (64 - hamming_distance) / 64 * 100)
```

**Strengths**: Robust to brightness/contrast changes, format independent
**Weaknesses**: Less effective on heavily cropped images

### Rule 3: Template Matching (0-60 points)
**Purpose**: Direct visual correlation using OpenCV

**Multi-scenario Matching**:
1. **Crop Detection**: Input as subset of original
2. **Reverse Crop**: Original as subset of input  
3. **Multi-scale Analysis**: Tests 5 different scale factors (0.5x to 1.5x)

**Technical Approach**:
- Uses `cv2.matchTemplate()` with normalized correlation coefficient
- Processes grayscale images for efficiency
- Applies `TM_CCOEFF_NORMED` method for 0-1 normalized results

**Quality Thresholds**:
- ≥0.9 correlation → Excellent Match
- 0.8-0.89 → Good Match  
- 0.6-0.79 → Moderate Match
- 0.3-0.59 → Weak Match
- <0.3 → No Match

**Strengths**: Excellent for detecting crops and geometric changes
**Weaknesses**: Computationally intensive, sensitive to significant modifications

---

## Setup and Installation

### Step 1: Environment Setup
```bash
# Create virtual environment (recommended)
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate

# Install dependencies
pip install pillow imagehash opencv-python numpy
```

### Step 2: Dataset Organization
Organize your dataset in this structure:
```
project/
├── forensics_detective.py    # Main expert system
├── rules.py                  # Three analysis rules  
├── test_system.py           # Testing framework
├── originals/               # Reference images (10 files)
├── modified_images/         # Modified test images (60 files)
└── random/                  # Random control images (5 files)
```

### Step 3: Dataset Acquisition
Download the official dataset:
```bash
git clone https://github.com/delveccj/EAS510_Assignment1.git
```
---

## How to Run the Project

### Basic Execution
```bash
python test_system.py
```

### Expected Output Format
```
Processing: modified_00_bright_enhanced.jpg
Rule 1 (Metadata): FIRED - METADATA_SIMILAR, Size ratio 0.97 → 25/30 points
Rule 2 (Image Hash): FIRED - EXCELLENT_MATCH - Best: 100.0% → 10/10 points  
Rule 3 (Template): FIRED - EXCELLENT_MATCH, Correlation: 0.990 → 59/60 points
Final Score: 94/100 → MATCH to original_00.jpg
```
---

## Performance Analysis & Results

### System Performance Metrics
Based on test results from `results.txt`:

| Metric | Value |
|--------|-------|
| **Overall Accuracy** | ~90% |
| **Modified Images Accuracy** | 100% (60/60 images correctly matched) |
| **Random Images Rejection** | 100% (5/5 images correctly rejected) |
| **Processing Speed** | ~0.5-1.0 seconds per image |

### Rule Effectiveness Analysis

#### Rule 1 (Metadata Analysis)
- **Most Effective For**: Format conversions, compression detection
- **Typical Scores**: 5-25 points
- **Key Insights**: 
  - PNG format conversions score lower due to metadata differences
  - Compressed images show reduced file sizes but maintain dimensions
  - 25% crops often result in 0 points due to significant size changes

#### Rule 2 (Image Hashing)
- **Most Effective For**: Brightness enhancement, format conversion, compression
- **Typical Scores**: 2-10 points  
- **Key Insights**:
  - **Brightness Enhancement**: Achieves 100% similarity across all hash types
  - **Compression**: Perfect 100% hash similarity despite file size reduction
  - **Format Conversion**: Maintains perfect hash similarity (JPEG→PNG)
  - **Crops**: Performance degrades with crop percentage (75% crop → 79% similarity, 25% crop → 51% similarity)

#### Rule 3 (Template Matching)
- **Most Effective For**: All modification types, especially crops
- **Typical Scores**: 59-60 points
- **Key Insights**:
  - Consistently high performance across all modification types
  - Excellent crop detection with 0.999 correlation scores
  - Multi-scale matching improves robustness
  - Carries the heaviest weight in final decisions

### Modification Type Performance

| Modification Type | Success Rate | Key Challenge |
|------------------|--------------|---------------|
| **Brightness Enhancement** | 100% | None - perfect detection |
| **Compression** | 100% | Metadata size changes |
| **Format Conversion (PNG)** | 100% | Metadata format differences |
| **75% Crops** | 100% | Reduced metadata scores |
| **50% Crops** | 100% | Hash similarity degradation |
| **25% Crops** | 100% | Severe metadata/hash score reduction |

---

## Technical Deep Dive

### Expert System Decision Logic
The system uses **linear score aggregation** with a fixed threshold:
```python
total_score = metadata_score + hash_score + template_score
decision = "MATCH" if total_score >= 60 else "REJECTED"
```

### Why This Approach Works
1. **Complementary Rules**: Each rule captures different aspects of similarity
2. **Weighted Contribution**: Template matching (60%) carries more weight than metadata (30%) and hashing (10%)
3. **Threshold Tuning**: 60-point threshold balances accuracy and false positive prevention
4. **Transparent Reasoning**: Each rule provides detailed evidence for forensic validation

### Key Design Decisions
- **Multiple Hash Types**: Increases robustness against different modification patterns
- **Multi-scale Template Matching**: Handles size variations effectively  
- **Evidence Preservation**: Maintains detailed reasoning chain for expert review
- **Graceful Degradation**: System continues operation even if individual rules fail

---

## Code Structure and Files

### Core Files Description

**`forensics_detective.py`** - Main Expert System
- `SimpleDetective` class implementing the expert system
- Target registration and signature computation
- Best match finding with evidence aggregation
- Metadata and hash extraction methods

**`rules.py`** - Analysis Rules Implementation  
- `check_metadata()` - File property analysis
- `check_hashes()` - Perceptual hash comparison
- `check_template()` - OpenCV template matching
- Helper functions for hash operations

**`test_system.py`** - Testing Framework
- Batch processing of test datasets
- Performance metrics calculation  
- Detailed output formatting
- Summary statistics generation

---

## Common Issues and Troubleshooting

### Dataset Issues
```bash
# Missing folder error
[ERROR] Originals folder 'originals' not found
# Solution: Ensure proper dataset structure and folder names
```

### Import Errors
```bash
# Missing libraries
ModuleNotFoundError: No module named 'imagehash'
# Solution: pip install imagehash opencv-python pillow
```

### Performance Issues
- **Slow Processing**: Reduce image sizes or limit scale factors in template matching
- **Memory Usage**: Close images properly, use grayscale conversion
- **Hash Errors**: Verify image file integrity and supported formats

---

## Future Improvements

### Potential Enhancements
1. **Machine Learning Integration**: Combine expert rules with ML confidence scoring
2. **Advanced Hash Algorithms**: Implement newer perceptual hashing methods
3. **Parallel Processing**: Multi-threading for batch analysis
4. **GUI Interface**: User-friendly graphical interface
5. **Database Integration**: Store signatures for large-scale forensic databases
6. **Advanced Metadata**: GPS data analysis, camera fingerprinting

### Research Directions
- **Deep Learning Features**: CNN-based visual feature extraction
- **Adversarial Robustness**: Detection of sophisticated image manipulations  
- **Real-time Analysis**: Optimization for live forensic scenarios
- **Multi-modal Analysis**: Integration of audio/video forensic techniques

---

## References and Further Reading

### Academic Sources
- Digital Image Forensics: A Survey of Recent Techniques
- Expert Systems in Artificial Intelligence
- Perceptual Hashing Algorithms for Image Authentication
- OpenCV Template Matching Documentation

### Technical Documentation
- [PIL/Pillow Documentation](https://pillow.readthedocs.io/)
- [ImageHash Library](https://pypi.org/project/ImageHash/)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

---

*This expert system demonstrates classical AI principles applied to digital forensics, providing transparent and reliable decision-making capabilities suitable for forensic applications.*
