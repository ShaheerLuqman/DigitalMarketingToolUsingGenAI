from PIL import Image, ImageDraw, ImageFont
import os
import svgwrite
import base64
import io

def resize_image(image: Image.Image, max_size: int) -> Image.Image:
    """Resize the image to a maximum of max_size while maintaining the aspect ratio."""
    width, height = image.size
    if width > height:
        # Width is greater, scale based on width
        scale_factor = max_size / width
    else:
        # Height is greater or equal, scale based on height
        scale_factor = max_size / height

    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def create_final_image(background_image: Image.Image, product_image: Image.Image, slogan: str, text_color: str) -> Image.Image:
    """Create a final image by overlaying the product image on the background and adding a slogan."""
    # Resize images to a maximum of 300 pixels while maintaining aspect ratio
    product_image = resize_image(product_image, 250)

    # Create a new image with the background
    final_image = background_image.copy()

    # Calculate position to center the product image
    bg_width, bg_height = final_image.size
    prod_width, prod_height = product_image.size
    position = ((bg_width - prod_width) // 2, (bg_height - prod_height) // 2)

    # Paste the product image onto the background
    final_image.paste(product_image, position, product_image)

    # Draw the slogan on the final image
    draw = ImageDraw.Draw(final_image)

    # Load the Berlin Sans FB font from the specified path
    font_path = r"C:\Windows\Fonts\BRLNSR.ttf"  # Use raw string to avoid escape issues
    font_size = 40  # Adjust the font size as needed

    try:
        font = ImageFont.truetype(font_path, font_size)
        print(f"Loaded font: {font_path} with size: {font_size}")
    except IOError:
        print(f"Error: Unable to load '{font_path}'. Using default font.")
        font = ImageFont.load_default()  # Fallback to default font

    # Calculate text size using textbbox
    text_bbox = draw.textbbox((0, 0), slogan, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Position the slogan at the bottom center
    text_position = ((bg_width - text_width) // 2, bg_height - text_height - 20)  # 20 pixels from the bottom
    draw.text(text_position, slogan, fill=text_color, font=font)  # Use text_color for the text

    return final_image

def pil_image_to_base64(image: Image.Image) -> str:
    """Convert a PIL image to a base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def save_as_svg(background_image: Image.Image, product_image: Image.Image, slogan: str, output_path: str):
    """Save the final image as a layered SVG."""
    dwg = svgwrite.Drawing(output_path, profile='tiny')

    # Convert images to base64
    bg_base64 = pil_image_to_base64(background_image)
    prod_base64 = pil_image_to_base64(product_image)

    # Add background image
    dwg.add(dwg.image(href=f"data:image/png;base64,{bg_base64}", insert=(0, 0), size=background_image.size))

    # Add product image
    prod_width, prod_height = product_image.size
    position = ((background_image.width - prod_width) // 2, (background_image.height - prod_height) // 2)
    dwg.add(dwg.image(href=f"data:image/png;base64,{prod_base64}", insert=position, size=product_image.size))

    # Add slogan text with Berlin Sans FB font
    dwg.add(dwg.text(slogan, insert=(background_image.width // 2, background_image.height - 20), text_anchor="middle", fill="black", font_size="40px", font_family="Berlin Sans FB"))

    # Save the SVG file
    dwg.save()

def save_as_png(image: Image.Image, output_path: str):
    """Save the image as a PNG file."""
    image.save(output_path, format="PNG")

if __name__ == "__main__":
    # Load images from the temp folder
    background_path = './temp/bg.png'
    product_path = './temp/product-nonbg.png'

    # Fixed slogan
    fixed_slogan = "Your Amazing Product!"

    try:
        # Load the background and product images
        background_image = Image.open(background_path)
        product_image = Image.open(product_path)

        # Create the final image
        final_image = create_final_image(background_image, product_image, fixed_slogan, "black")

        # Display the final image
        final_image.show()

        # Save the final image as a layered SVG
        svg_output_path = './temp/final_image.svg'
        save_as_svg(background_image, product_image, fixed_slogan, svg_output_path)
        print(f"Final image created and saved as '{svg_output_path}'.")

        # Save the final image as PNG
        png_output_path = './temp/final_image.png'
        save_as_png(final_image, png_output_path)
        print(f"Final image created and saved as '{png_output_path}'.")

    except Exception as e:
        print(f"Error processing images: {e}")