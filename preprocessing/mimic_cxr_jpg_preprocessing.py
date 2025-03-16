import os
import argparse
from PIL import Image
from multiprocessing import Pool, cpu_count

# Function to process a single image
def process_image(input_output_paths):
    image_path, output_path = input_output_paths
    
    try:
        # Open image
        img = Image.open(image_path).convert("RGB")

        # Step 1: Resize while preserving aspect ratio
        img.thumbnail((512, 512), Image.LANCZOS)

        # Step 2: Center crop with padding (black background)
        new_img = Image.new("RGB", (512, 512), (0, 0, 0))  # Black background
        x_offset = (512 - img.width) // 2
        y_offset = (512 - img.height) // 2
        new_img.paste(img, (x_offset, y_offset))

        # Save processed image
        new_img.save(output_path)
        return f"Processed: {output_path}"
    except Exception as e:
        return f"Error processing {image_path}: {e}"

# Function to create directories and process images in parallel
def process_images_parallel(process_folder):
    # Define output folder path
    output_folder = f"{process_folder}_processed"
    os.makedirs(output_folder, exist_ok=True)

    # Collect all .jpg files from process_folder recursively
    image_paths = []
    for root, dirs, files in os.walk(process_folder):
        for file in files:
            if file.lower().endswith(".jpg"):
                # Calculate output path by replicating folder structure in output folder
                relative_path = os.path.relpath(root, process_folder)
                output_path = os.path.join(output_folder, relative_path, file)

                # Ensure the output folder structure exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Add the input-output pair
                image_paths.append((os.path.join(root, file), output_path))
    
    print(f'Total images to process: {len(image_paths)}')
    
    # Use multiprocessing to process images in parallel
    with Pool(processes=cpu_count()) as pool:
        print(f'Using {cpu_count()} cpu cores')# Uses all available CPU cores
        results = pool.map(process_image, image_paths)
    
    print(f'Processed {len(results)} images')

# Main function to handle command-line arguments
def main():
    parser = argparse.ArgumentParser(description="Process images in a folder with multiprocessing.")
    parser.add_argument('--process_folder', type=str, required=True, help="Path to the folder to process")
    
    args = parser.parse_args()
    
    # Run the image processing
    process_images_parallel(args.process_folder)

# Entry point for the script
if __name__ == "__main__":
    main()