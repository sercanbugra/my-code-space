import os
from PIL import Image

# Function to crop the bottom 85% of an image (keep only the top 15%)
def crop_top_15_percent(image_path, output_path):
    img = Image.open(image_path)
    width, height = img.size

    # Calculate the height to keep (top 15%)
    keep_height = int(height * 0.15)

    # Crop the image to keep the top 15%
    cropped_img = img.crop((0, 0, width, keep_height))
    
    # Save the cropped image
    cropped_img.save(output_path)

# Folder paths (use raw strings to avoid unicode errors)
input_folder = r"C:\path\to\input_folder"  # Replace with your input folder path
output_folder = r"C:\path\to\output_folder"  # Replace with your output folder path

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Iterate through all files in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):  # Filter image files
        input_file_path = os.path.join(input_folder, filename)
        output_file_path = os.path.join(output_folder, filename)

        # Crop the image and save it
        crop_top_15_percent(input_file_path, output_file_path)

print("Cropping completed!")
