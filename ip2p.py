import PIL
import requests
import torch
from diffusers import StableDiffusionInstructPix2PixPipeline, EulerAncestralDiscreteScheduler

# Load the model and pipeline
model_id = "timbrooks/instruct-pix2pix"
pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    model_id, torch_dtype=torch.float16, revision="fp16", safety_checker=None
)
pipe.to("cuda")
pipe.enable_attention_slicing()

# Load and preprocess the input image
image = PIL.Image.open("./temp/24 (1).png")
image = PIL.ImageOps.exif_transpose(image)
image = image.convert("RGB")

# Define the prompt and run the pipeline
prompt = "Recolor the image with Maastricht Blue"
result_image = pipe(prompt, image=image, num_inference_steps=20, image_guidance_scale=1).images[0]

# Save the processed image
result_image.save("./temp/processed_image.png")

print("Processed image saved as './temp/processed_image.png'")
