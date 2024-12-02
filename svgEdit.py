# https://colab.research.google.com/github/huggingface/notebooks/blob/main/diffusers/InstructPix2Pix_using_diffusers.ipynb#scrollTo=1aRurg5CBe82

from PIL import Image
import svgwrite
import base64
from io import BytesIO

def png_to_base64(png_file_path):
    # Convert PNG to base64
    with open(png_file_path, "rb") as png_file:
        return f"data:image/png;base64,{base64.b64encode(png_file.read()).decode('utf-8')}"

def create_svg_with_layers(png_file1, png_file2, output_svg):
    # Create an SVG drawing
    dwg = svgwrite.Drawing(output_svg, profile='tiny', size=("500px", "500px"))
    
    # Convert PNG files to base64
    png_base64_1 = png_to_base64(png_file1)
    png_base64_2 = png_to_base64(png_file2)

    # Add the images as layers
    dwg.add(dwg.image(png_base64_1, insert=(0, 0), size=("500px", "500px")))
    dwg.add(dwg.image(png_base64_2, insert=(0, 0), size=("500px", "500px")))

    # Save the SVG file
    dwg.save()

# Example usage
create_svg_with_layers("temp\\preview.png", "temp\\product-nonbg.png", "output_image.svg")
