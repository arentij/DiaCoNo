from PIL import Image
import os


def create_gif_from_images(folder_path, output_gif_path, duration=500):
    # Collect all .jpg files in the folder
    images = []
    for filename in sorted(os.listdir(folder_path)):
        print(filename)
        if filename.lower().endswith('.jpg'):
            file_path = os.path.join(folder_path, filename)
            try:
                img = Image.open(file_path)
                images.append(img)
            except IOError:
                print(f"Unable to open image file {file_path}")

    if not images:
        print("No images found in the specified folder.")
        return

    # Save images as a GIF
    images[0].save(output_gif_path, save_all=True, append_images=images[1:], duration=duration, loop=0)
    print(f"GIF created successfully and saved to {output_gif_path}")


# Example usage
folder_path = '/CMFX_RAW/video/CMFX_01212/video12/boom/video12'  # Change this to your folder path
output_gif_path = 'output.gif'  # Change this to your desired output path
create_gif_from_images(folder_path, output_gif_path)
