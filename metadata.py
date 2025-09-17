from PIL import Image, ExifTags

# Open image
img = Image.open(r"data\originals\original_00.jpg")

# Get EXIF metadata
exif_data = img._getexif()

if exif_data is not None:
    exif = {
        ExifTags.TAGS.get(k, k): v
        for k, v in exif_data.items()
    }
    print(exif)
else:
    print("No EXIF metadata found in this image.")
