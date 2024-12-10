from diffusers import DiffusionPipeline
from PIL import Image, ImageOps
import torch

# Load pre-trained model pipeline
model_id = "yahoo-inc/photo-background-generation"
pipeline = DiffusionPipeline.from_pretrained(model_id, custom_pipeline=model_id)
pipeline = pipeline.to('cuda')

# Helper function to resize image with padding
def resize_with_padding(img, expected_size):
    img.thumbnail((expected_size[0], expected_size[1]))
    delta_width = expected_size[0] - img.size[0]
    delta_height = expected_size[1] - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (pad_width, pad_height, delta_width - pad_width, delta_height - pad_height)
    return ImageOps.expand(img, padding)

# Load the background-removed image
img = Image.open("temp/product-nonbg.png")
img = resize_with_padding(img, (512, 512))

# Generate mask (you can also directly provide your mask if available)
mask = ImageOps.invert(img.convert("L"))  # Example: create a mask based on the image's alpha or brightness

# Diffusion parameters
seed = 13
prompt = 'Abstract professional'
cond_scale = 1.0
generator = torch.Generator(device='cuda').manual_seed(seed)

# Generate image
with torch.autocast("cuda"):
    controlnet_image = pipeline(
        prompt=prompt,
        image=img,
        mask_image=mask,
        control_image=mask,
        num_images_per_prompt=1,
        generator=generator,
        num_inference_steps=20,
        guess_mode=False,
        controlnet_conditioning_scale=cond_scale
    ).images[0]

# Save or display the resulting image
controlnet_image.show()
controlnet_image.save("generated_image.png")
