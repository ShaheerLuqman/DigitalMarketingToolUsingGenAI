from PIL import Image, ImageOps
import pandas as pd
import numpy as np
import colorsys
from sklearn.cluster import KMeans
from colory.color import Color
import torch
from diffusers import StableDiffusionInstructPix2PixPipeline
import warnings
import os
import random
import shutil
import io
import google.generativeai as genai

# Suppress specific warning
warnings.filterwarnings(
    "ignore",
    message="You have disabled the safety checker",
    category=UserWarning
)

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_contrasting_color(color_names):
    """Ask Gemini for a contrasting color to the list of color names provided."""
    colors = []
    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    f"I have product with {color_names} color. No description please Just give me name of 1 basic combine color for the whole list."
                ],
            },
        ]
    )
    
    response = chat_session.send_message("INSERT_INPUT_HERE")
    color = response.text.strip()  # Ensure this is a string
    
    comp_response = chat_session.send_message(f"What color complements {color}? Give a single name.")
    color += ", " + comp_response.text.strip()
    colors.append(color)  # Append the complementary color

    # Ask for text color
    text_color_response = chat_session.send_message(f"What color of Text black or white will suit on {color}? Give a single name.")
    colors.append(text_color_response.text.strip())  # Append the text color

    return colors  # Return both contrasting and complementary colors

def get_palette(image):
    """Modified to accept PIL Image object instead of path"""
    reduced_image = image.convert("P", palette=Image.Palette.WEB)
    palette = reduced_image.getpalette()
    palette = [palette[i:i+3] for i in range(0, len(palette), 3)]
    return reduced_image, palette

def count_color_frequencies(reduced_image, palette):
    color_count = [(count, palette[color_index]) for count, color_index in reduced_image.getcolors()]
    return pd.DataFrame(color_count, columns=['cnt', 'RGB'])

def rgb_to_hex(red, green, blue):
    return f'#{red:02x}{green:02x}{blue:02x}'

def rgb_to_hsl_hue(r, g, b):
    h, _, _ = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return str(int(round(h * 359)))

def cluster_and_get_top_colors(df):
    kmeans_hsl = KMeans(n_clusters=2, random_state=42)
    df['cluster_hsl'] = kmeans_hsl.fit_predict(df[['hsl']])
    top_colors_hsl = df.groupby('cluster_hsl').head(1).reset_index(drop=True)
    return top_colors_hsl

def extract_colors(image):
    """Modified to accept PIL Image object instead of path"""
    reduced_image, palette = get_palette(image)
    color_count_df = count_color_frequencies(reduced_image, palette)
    
    # Get top 6 most frequent colors
    color_count_df = color_count_df.sort_values(by='cnt', ascending=False).iloc[:6]
    
    RGB = pd.DataFrame(color_count_df['RGB'].to_list(), columns=['r', 'g', 'b'])
    RGB['hex'] = RGB.apply(lambda r: rgb_to_hex(*r), axis=1)
    RGB = RGB[RGB['hex'] != '#000000']  # Remove black
    
    RGB['hsl'] = RGB.apply(lambda r: rgb_to_hsl_hue(r['r'], r['g'], r['b']), axis=1)
    top_colors = cluster_and_get_top_colors(RGB)
    top_colors.drop(['cluster_hsl'], axis=1, inplace=True)

    # Add complementary color if only one color is found
    if len(top_colors) == 1:
        dominant_color = top_colors.iloc[0]
        r, g, b = dominant_color['r'], dominant_color['g'], dominant_color['b']
        comp_r, comp_g, comp_b = np.round(255 - r), np.round(255 - g), np.round(255 - b)
        complementary_row = {
            'r': comp_r, 'g': comp_g, 'b': comp_b, 
            'hex': rgb_to_hex(int(comp_r), int(comp_g), int(comp_b))
        }
        top_colors = pd.concat([top_colors, pd.DataFrame([complementary_row])], ignore_index=True)

    # Convert hex colors to color names
    color_names = [Color(hex_color, 'wiki').name for hex_color in top_colors.hex.to_list()]
    return color_names

def recolor_image(input_image: Image.Image, prompt: str, num_inference_steps: int = 20, image_guidance_scale: float = 1.0) -> Image.Image:
    model_id = "timbrooks/instruct-pix2pix"
    pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(
        model_id, torch_dtype=torch.float16, revision="fp16", safety_checker=None
    )
    pipe.to("cuda")
    pipe.enable_attention_slicing()

    # Preprocess the input image
    image = input_image.copy()
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")

    # Run the pipeline with the prompt
    result_image = pipe(
        prompt, 
        image=image, 
        num_inference_steps=num_inference_steps, 
        image_guidance_scale=image_guidance_scale
    ).images[0]
    
    return result_image

def get_random_background():
    # Create used folder if it doesn't exist
    used_folder = 'bg_dataset/used'
    os.makedirs(used_folder, exist_ok=True)
    
    # Get list of available background images
    bg_folder = 'bg_dataset'
    available_bgs = [f for f in os.listdir(bg_folder) 
                    if f.endswith(('.png', '.jpg', '.jpeg')) 
                    and os.path.isfile(os.path.join(bg_folder, f))]
    
    if not available_bgs:
        raise Exception("No background images available! Please add more images to bg_dataset folder.")
    
    # Randomly select a background
    selected_bg = random.choice(available_bgs)
    bg_path = os.path.join(bg_folder, selected_bg)
    
    # Move to used folder
    used_path = os.path.join(used_folder, selected_bg)
    shutil.move(bg_path, used_path)
    
    return used_path

def process_product_image(product_image: Image.Image, output_path: str = None) -> tuple[Image.Image, str]:
    """Modified to accept PIL Image object and optionally return PIL Image and text color"""
    # Extract colors from the product image
    color_names = extract_colors(product_image)
    color_names = (",").join(color_names)
    
    # Print extracted colors
    print(color_names)
    # Get suggested background color from Gemini
    suggested_color = get_contrasting_color(color_names)
    
    # Create prompt using extracted colors and suggested background color
    prompt = f"Recolor the image to shades of {suggested_color[0]}, keeping textures and details intact."
    text_color = suggested_color[1]  # Store the text color
    print(text_color)
    
    # Get random background image
    background_image_path = get_random_background()
    print(f"Selected background: {os.path.basename(background_image_path)}")
    
    # Load and process the background image
    background_image = Image.open(background_image_path)
    # Resize background to 500x500 pixels
    background_image = background_image.resize((500, 500), Image.Resampling.LANCZOS)
    processed_image = recolor_image(background_image, prompt)
    
    # Save the processed image if output_path is provided
    if output_path:
        processed_image.save(output_path)
        print(f"✓ Processed image saved as: {output_path}")
    
    return processed_image, text_color  # Return both processed image and text color

if __name__ == "__main__":
    # Load product image as PIL object
    product_image_path = './temp/temp.jpg'
    output_path = './temp/bg.png'
    
    try:
        # Load the product image as PIL object
        product_image = Image.open(product_image_path)
        
        # Process the image and get the result
        processed_image, text_color = process_product_image(product_image, output_path)
        
        # Display the result (optional)
        processed_image.show()
        
        print("Processing completed successfully!")
        
    except Exception as e:
        print(f"Error processing image: {e}")
