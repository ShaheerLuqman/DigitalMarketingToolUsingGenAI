import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import shutil
from rembg import remove
import threading
from tkinter import ttk
from bg_generator import process_product_image
from dotenv import load_dotenv
from finalPost import create_final_image, save_as_svg, save_as_png
from datetime import datetime
import warnings
import webbrowser
import google.generativeai as genai

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()

class ProductApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Info App")

        # Initialize text_color
        self.text_color = "white"  # Initialize text_color

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set window size and position it 100px below the top
        self.root.geometry(f"1600x900+{int((screen_width - 1600) / 2)}+50")

        # Initialize other variables
        self.image_path = ""
        self.description = ""
        self.product_name = ""

        # Title
        self.title_label = tk.Label(self.root, text="Product Information", font=("Helvetica", 24))
        self.title_label.pack(pady=20)

        # Form frame
        self.form_frame = tk.Frame(self.root)
        self.form_frame.pack(pady=10)

        # Product Name Label and Entry
        self.name_label = tk.Label(self.form_frame, text="Enter product name:", font=("Helvetica", 14))
        self.name_label.pack(pady=5)

        self.name_entry = tk.Entry(self.form_frame, width=50, font=("Helvetica", 14))
        self.name_entry.pack(pady=5)

        # Upload Image Button
        self.upload_button = tk.Button(self.form_frame, text="Upload Product Image", font=("Helvetica", 14), command=self.upload_image)
        self.upload_button.pack(pady=10)

        # Description Label and Textbox
        self.description_label = tk.Label(self.form_frame, text="Enter product description:", font=("Helvetica", 14))
        self.description_label.pack(pady=5)

        self.description_entry = tk.Entry(self.form_frame, width=50, font=("Helvetica", 14))
        self.description_entry.pack(pady=5)

        # Image thumbnail label (initially None)
        self.thumbnail_label = None

        # Display Area (initially hidden)
        self.display_frame = tk.Frame(self.root)

        # Image and description labels (initially set to None)
        self.img_label = None
        self.desc_label = None
        self.back_button = None  # Initialize the back button here

        # Add page indicator frame at the bottom
        self.page_indicator_frame = tk.Frame(self.root)
        self.page_indicator_frame.pack(side=tk.BOTTOM, pady=10)
        
        self.page_label = tk.Label(self.page_indicator_frame, text="Page 1 of 6", font=("Helvetica", 12))
        self.page_label.pack()

        # Bottom Button Frame for Back and Next buttons (move it above page indicator)
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        # Back Button (Initially disabled)
        self.back_button = tk.Button(self.bottom_frame, text="Back", font=("Helvetica", 14), state=tk.DISABLED, command=self.go_back)
        self.back_button.pack(side=tk.LEFT, padx=20)

        # Next Button (Initially enabled)
        self.next_button = tk.Button(self.bottom_frame, text="Next", font=("Helvetica", 14), state=tk.DISABLED, command=self.display_product_info)
        self.next_button.pack(side=tk.RIGHT, padx=20)

        # Initialize additional variable for processed image
        self.processed_image_path = None

        # Initialize loading spinner (but don't pack it yet)
        self.loading_spinner = ttk.Progressbar(self.display_frame, mode='indeterminate')
        
        # Initialize background image path
        self.background_image_path = None

        # Initialize slogan and caption variables
        self.slogan = ""
        self.caption = ""

    
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.generation_config,
        )
        self.chat_session = None

    def upload_image(self):
        """Upload image file"""
        # Ask the user to select a new image
        new_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

        if new_image_path:
            # Create temp directory if it doesn't exist
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)

            # Delete existing product-og file if it exists
            existing_files = [f for f in os.listdir(temp_dir) if f.startswith("product-og")]
            if existing_files:
                os.remove(os.path.join(temp_dir, existing_files[0]))

            # Get file extension from original file
            _, ext = os.path.splitext(new_image_path)
            
            # Create new path in temp directory
            self.image_path = os.path.join(temp_dir, f"product-og{ext}")

            # Copy the image to temp directory
            shutil.copy2(new_image_path, self.image_path)

            # Remove previous thumbnail if it exists
            if self.thumbnail_label:
                self.thumbnail_label.pack_forget()
                self.root.update_idletasks()

            # Create and display the new thumbnail
            img = Image.open(self.image_path)
            img.thumbnail((100, 100))
            img = ImageTk.PhotoImage(img)

            # Create a new label for the thumbnail and insert it before description
            self.thumbnail_label = tk.Label(self.form_frame, image=img)
            self.thumbnail_label.image = img
            
            # Pack the thumbnail before the description label
            self.description_label.pack_forget()
            self.description_entry.pack_forget()
            
            self.thumbnail_label.pack(pady=10)
            
            # Repack the description elements
            self.description_label.pack(pady=5)
            self.description_entry.pack(pady=5)

            # Enable the Next button after image upload
            self.next_button.config(state=tk.NORMAL)

    def display_product_info(self):
        """Display the product image and description"""
        self.product_name = self.name_entry.get()
        self.description = self.description_entry.get()

        if not self.image_path or not self.description or not self.product_name:
            tk.messagebox.showerror("Error", "Please provide product name, image and description!")
            return

        # Hide form and show display frame
        self.form_frame.pack_forget()
        
        # Clear the display frame first
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        
        self.display_frame.pack(pady=20)

        # Change the heading text to "Your Submission"
        self.title_label.config(text="Your Submission")

        # Create and display the product name at the top
        self.name_label = tk.Label(self.display_frame, text=self.product_name, font=("Helvetica", 18, "bold"))
        self.name_label.pack(pady=(0, 10))

        # Load and display the image
        img = Image.open(self.image_path)
        img.thumbnail((700, 700))  # Resize the image to fit within the 700x700 box
        img = ImageTk.PhotoImage(img)

        self.img_label = tk.Label(self.display_frame, image=img)
        self.img_label.image = img  # Keep a reference to the image object
        self.img_label.pack(pady=20)

        # Display the description below the image
        self.desc_label = tk.Label(self.display_frame, text="Description: " + self.description, font=("Helvetica", 14), wraplength=1200)
        self.desc_label.pack(pady=10)

        # Disable Next button and keep Back button enabled when on the last page
        self.next_button.config(state=tk.DISABLED)
        self.back_button.config(state=tk.NORMAL)

        # Update page indicator
        self.update_page_number(2)

        # Enable Next button when moving to background removal page
        self.next_button.config(state=tk.NORMAL, command=self.remove_background)

    def go_back(self):
        """Go back to the previous page"""
        current_page = int(self.page_label.cget("text").split()[1])
        
        if current_page == 6:  # If on final post page
            # Clear the display frame
            for widget in self.display_frame.winfo_children():
                widget.destroy()

            # Change the heading text
            self.title_label.config(text="Generate Text")
            
            # Create and show text generator page
            self.show_text_generator()
            
            # Update page indicator
            self.update_page_number(5)
            
        elif current_page == 5:  # If on text generation page
            if hasattr(self, 'slogan_text') and hasattr(self, 'caption_text'):
                self.slogan = self.slogan_text.get("1.0", tk.END).strip()
                self.caption = self.caption_text.get("1.0", tk.END).strip()
            self.show_background_generator()
            self.next_button.config(state=tk.NORMAL, command=self.show_text_generator)
            self.update_page_number(4)
        elif current_page == 4:  # If on background generator page
            # Clear the display frame
            for widget in self.display_frame.winfo_children():
                widget.destroy()
            
            # Change the heading text
            self.title_label.config(text="Background Removed")

            # Load and display the processed image
            img = Image.open(self.processed_image_path)
            img.thumbnail((700, 700))
            img = ImageTk.PhotoImage(img)

            # Create generate button
            generate_button = tk.Button(
                self.display_frame, 
                text="Generate New Background", 
                font=("Helvetica", 14),
                command=self.generate_background
            )
            generate_button.pack(pady=20)

            self.img_label = tk.Label(self.display_frame, image=img)
            self.img_label.image = img
            self.img_label.pack(pady=20)

            # Update button states
            self.next_button.config(state=tk.NORMAL, command=self.show_background_generator)
            self.back_button.config(state=tk.NORMAL)

            # Update page indicator
            self.update_page_number(3)
            
            # Reset background image path
            self.background_image_path = None
        elif current_page == 3:  # If on background removal page
            self.processed_image_path = None
            self.display_product_info()  # Go back to page 2
            self.update_page_number(2)
        else:  # If on page 2
            self.display_frame.pack_forget()
            self.form_frame.pack(pady=10)
            self.title_label.config(text="Product Information")
            self.back_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.NORMAL, command=self.display_product_info)
            self.update_page_number(1)

    def remove_background(self):
        """Display the product image with background removed"""
        # Clear the display frame
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # Change the heading text
        self.title_label.config(text="Processing Image...")

        # Show loading spinner
        self.loading_spinner = ttk.Progressbar(self.display_frame, mode='indeterminate')
        self.loading_spinner.pack(pady=20)
        self.loading_spinner.start(10)  # Start the animation
        
        # Disable both buttons during processing
        self.next_button.config(state=tk.DISABLED)
        self.back_button.config(state=tk.DISABLED)
        
        # Process in background thread
        thread = threading.Thread(target=self._process_background_removal)
        thread.start()
        
    def _process_background_removal(self):
        """Process background removal in background thread"""
        # Get the input image path and extension
        input_name, input_ext = os.path.splitext(self.image_path)
        if not input_ext:
            input_ext = '.png'

        # Create output path in temp directory
        output_path = os.path.join('temp', 'product-nonbg.png')

        # Remove background using rembg
        input_img = Image.open(self.image_path)
        output_img = remove(input_img, only_mask=False)
        
        # Convert to RGBA if not already
        output_img = output_img.convert("RGBA")
        
        # Find the bounding box of the non-transparent area
        bbox = output_img.getbbox()
        
        if bbox:
            # Crop the non-transparent area
            output_img = output_img.crop(bbox)
            
            # Get original dimensions
            original_width, original_height = output_img.size
            
            # Calculate scaling factor to maintain aspect ratio
            scaling_factor = min(300 / original_width, 300 / original_height)
            
            # Calculate new dimensions
            new_width = int(original_width * scaling_factor)
            new_height = int(original_height * scaling_factor)
            
            # Resize the image
            output_img = output_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save the processed image
        output_img.save(output_path, "PNG")
        self.processed_image_path = output_path
        
        # Schedule UI update on main thread
        self.root.after(0, self._finish_background_removal)
        
    def _finish_background_removal(self):
        """Update UI after background removal is complete"""
        # Remove loading spinner
        self.loading_spinner.stop()
        self.loading_spinner.pack_forget()
        
        # Change the heading text
        self.title_label.config(text="Background Removed")

        # Load and display the processed image
        img = Image.open(self.processed_image_path)
        img.thumbnail((700, 700))
        img = ImageTk.PhotoImage(img)

        self.img_label = tk.Label(self.display_frame, image=img)
        self.img_label.image = img
        self.img_label.pack(pady=20)

        # Update button states
        self.next_button.config(state=tk.NORMAL, command=self.show_background_generator)
        self.back_button.config(state=tk.NORMAL)

        # Update page indicator
        self.update_page_number(3)

    def show_background_generator(self):
        """Show the background generation page"""
        # Clear the display frame
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # Change the heading text
        self.title_label.config(text="Generate Background")

        # Create generate button
        generate_button = tk.Button(
            self.display_frame, 
            text="Generate New Background", 
            font=("Helvetica", 14),
            command=self.generate_background
        )
        generate_button.pack(pady=20)

        # Check for existing background in temp folder
        temp_bg_path = os.path.join("temp", "bg.png")
        if os.path.exists(temp_bg_path):
            self.background_image_path = temp_bg_path
            self.display_background_image()

        # Update button states
        self.next_button.config(state=tk.NORMAL)
        self.back_button.config(state=tk.NORMAL)

        # Update page indicator
        self.update_page_number(4)

        # Update next button
        self.next_button.config(command=self.show_text_generator)

    def generate_background(self):
        """Generate and display background"""
        # Clear previous images except the generate button
        for widget in self.display_frame.winfo_children():
            if isinstance(widget, tk.Label) and hasattr(widget, 'image'):
                widget.destroy()
        
        # Show loading spinner
        self.loading_spinner = ttk.Progressbar(self.display_frame, mode='indeterminate')
        self.loading_spinner.pack(pady=20)
        self.loading_spinner.start(10)
        
        # Disable buttons during processing
        self.next_button.config(state=tk.DISABLED)
        self.back_button.config(state=tk.DISABLED)
        for widget in self.display_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.DISABLED)
        
        # Process in background thread
        thread = threading.Thread(target=self._process_background_generation)
        thread.start()

    def _process_background_generation(self):
        """Process background generation in background thread"""
        try:
            # Load the processed image
            product_image = Image.open(self.processed_image_path)
            
            # Set output path
            output_path = os.path.join("temp", "bg.png")
            
            # Generate background using bg_generator
            processed_image, text_color = process_product_image(product_image, output_path)
            
            self.text_color = text_color
            # Store the background image path
            self.background_image_path = output_path
            
            # Schedule UI update on main thread
            self.root.after(0, self._finish_background_generation)
        except Exception as e:
            print(f"Error generating background: {e}")
            # Schedule error handling on main thread
            self.root.after(0, self._handle_background_generation_error)

    def _finish_background_generation(self):
        """Update UI after background generation is complete"""
        # Remove loading spinner
        self.loading_spinner.stop()
        self.loading_spinner.pack_forget()
        
        # Re-enable buttons
        self.next_button.config(state=tk.NORMAL)
        self.back_button.config(state=tk.NORMAL)
        for widget in self.display_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.NORMAL)
        
        # Display the generated background
        if os.path.exists(self.background_image_path):
            bg_img = Image.open(self.background_image_path)
            bg_img.thumbnail((700, 700))
            bg_photo = ImageTk.PhotoImage(bg_img)
            
            bg_label = tk.Label(self.display_frame, image=bg_photo)
            bg_label.image = bg_photo
            bg_label.pack(pady=20)

    def _handle_background_generation_error(self):
        """Handle errors in background generation"""
        # Remove loading spinner
        self.loading_spinner.stop()
        self.loading_spinner.pack_forget()
        
        # Re-enable buttons
        self.next_button.config(state=tk.NORMAL)
        self.back_button.config(state=tk.NORMAL)
        for widget in self.display_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.NORMAL)
        
        # Show error message
        tk.messagebox.showerror("Error", "Failed to generate background. Please try again.")

    def display_background_image(self):
        """Display the generated background image"""
        if self.background_image_path and os.path.exists(self.background_image_path):
            # Remove previous image if exists
            for widget in self.display_frame.winfo_children():
                if isinstance(widget, tk.Label) and hasattr(widget, 'image'):
                    widget.destroy()

            # Load and display the background image
            img = Image.open(self.background_image_path)
            img.thumbnail((700, 700))
            img = ImageTk.PhotoImage(img)

            bg_label = tk.Label(self.display_frame, image=img)
            bg_label.image = img
            bg_label.pack(pady=20)

    def generate_slogan(self):
        """Generate slogan using Gemini AI"""
        try:
            if not self.chat_session:
                # Upload the processed image
                file = genai.upload_file(self.processed_image_path, mime_type="image/png")
                
                # Initialize chat session
                self.chat_session = self.model.start_chat()
                
                # Send the first message and get response
                response = self.chat_session.send_message([
                    file,
                    "Write a slogan of less than 4 words for the product. Slogan should be catchy and memorable. Return only one slogan and no punctuation marks."
                ]).text
            else:
                # Get another slogan if chat session exists
                response = self.chat_session.send_message("Give me another slogan").text
            
            return response
                
        except Exception as e:
            print(f"Error generating slogan: {e}")
            return "Error generating slogan"

    def generate_caption(self):
        """Generate a caption using Gemini with loading animation"""
        def task():
            self.show_loading("Generating caption...")
            try:
                if not hasattr(self, 'chat_session') or self.chat_session is None:
                    # Upload the image to Gemini
                    file = genai.upload_file(self.processed_image_path, mime_type="image/png")
                    
                    # Initialize chat session
                    self.chat_session = self.model.start_chat()
                    
                    if self.chat_session is None:
                        raise ValueError("Failed to start chat session. Please check your model configuration.")
                    
                    # Send the first message and get response
                    response = self.chat_session.send_message([
                        file,
                        f"Generate a caption for the product image. Product Name is {self.product_name} The caption should be descriptive and engaging. Caption should be of around 100 words. Include 3-4 Hashtags. Do not give options, just give one as output"
                    ]).text
                else:
                    # Get another caption if chat session exists
                    response = self.chat_session.send_message(f"Generate a caption for the product image. Product Name is {self.product_name} The caption should be descriptive and engaging. Caption should be of around 100 words. Include 3-4 Hashtags. Do not give options, just give one as output").text
                
                self.caption_text.insert(1.0, response)
            except Exception as e:
                print(f"Error generating caption: {e}")
                self.caption_text.insert(1.0, "Error generating caption.")
            finally:
                self.hide_loading()

        # Run the task in a separate thread to avoid blocking the UI
        threading.Thread(target=task).start()

    def show_text_generator(self):
        """Show the text generation page"""
        # Clear the display frame
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # Change the heading text
        self.title_label.config(text="Generate Text")

        # Create frame for slogan section
        slogan_frame = tk.Frame(self.display_frame)
        slogan_frame.pack(pady=20, fill=tk.X, padx=20)

        # Create loading spinner for slogan (but don't pack it yet)
        self.slogan_loading = ttk.Progressbar(slogan_frame, mode='indeterminate')

        # Create slogan button and text box
        generate_slogan_btn = tk.Button(
            slogan_frame,
            text="Generate Slogan",
            font=("Helvetica", 14),
            command=self.generate_slogan_with_loading
        )
        generate_slogan_btn.pack(pady=(0, 10))

        # Create and store slogan text widget reference first
        self.slogan_text = tk.Text(slogan_frame, height=3, width=70, font=("Helvetica", 12))
        self.slogan_text.pack()
        if self.slogan:
            self.slogan_text.insert(1.0, self.slogan)

        # Create frame for caption section
        caption_frame = tk.Frame(self.display_frame)
        caption_frame.pack(pady=20, fill=tk.X, padx=20)

        # Create and store caption text widget reference first
        self.caption_text = tk.Text(caption_frame, height=15, width=70, font=("Helvetica", 12))
        self.caption_text.pack()

        # Create caption button and text box
        generate_caption_btn = tk.Button(
            caption_frame,
            text="Generate Caption",
            font=("Helvetica", 14),
            command=self.generate_caption
        )
        generate_caption_btn.pack(pady=(0, 10))

        if self.caption:
            self.caption_text.insert(1.0, self.caption)

        # Update button states
        self.next_button.config(state=tk.NORMAL, command=self.show_final_post)
        self.back_button.config(state=tk.NORMAL)

        # Update page indicator
        self.update_page_number(5)

    def generate_post(self):
        """Placeholder function to generate final post"""
        return os.path.join("temp", "output_image.svg")

    def show_final_post(self):
        """Show the final generated post"""
        # Save the text content before moving to final page
        if hasattr(self, 'slogan_text') and hasattr(self, 'caption_text'):
            self.slogan = self.slogan_text.get("1.0", tk.END).strip()
            self.caption = self.caption_text.get("1.0", tk.END).strip()

        # Clear the display frame
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # Change the heading text
        self.title_label.config(text="Final Post")

        # Create the final image and get the path
        final_image_path = self.create_final_image(text_color="black")

        # Load and display the final image
        img = Image.open(final_image_path)
        img.thumbnail((500, 500))  # Reduced size to 500x500
        img = ImageTk.PhotoImage(img)

        # Create a label to display the final image
        final_img_label = tk.Label(self.display_frame, image=img)
        final_img_label.image = img  # Keep a reference to avoid garbage collection
        final_img_label.pack(pady=10)  # Adjusted padding

        # Display the caption below the final image
        caption_label = tk.Label(self.display_frame, text=self.caption, font=("Helvetica", 12), wraplength=1200, anchor='n', justify='left')
        caption_label.pack(pady=(10, 20))  # Adjusted padding for top and bottom

        # Rename Next Button to Finish
        self.next_button.config(text="Finish", command=self.finish_app)
        self.next_button.pack(pady=20)

        # Create a frame to hold the buttons
        button_frame = tk.Frame(self.display_frame)
        button_frame.pack(pady=10)

        # Create Save SVG Button with fixed size
        save_svg_button = tk.Button(button_frame, text="Save SVG", font=("Helvetica", 14), command=self.save_svg, width=20)
        save_svg_button.pack(side=tk.LEFT, padx=5)  # Add padding to the left

        # Create Open Boxy SVG Button
        open_boxy_svg_button = tk.Button(button_frame, text="Edit Your File", font=("Helvetica", 14), command=self.open_boxy_svg, width=20)
        open_boxy_svg_button.pack(side=tk.LEFT, padx=5)  # Add padding to the left

        # Update button states
        self.back_button.config(state=tk.NORMAL)  # Keep back button enabled

        # Update page indicator
        self.update_page_number(6)

    def save_svg(self):
        """Save the SVG file to a new location"""
        # Ask the user for a file path to save the SVG
        svg_output_path = filedialog.asksaveasfilename(defaultextension=".svg",
                                                        filetypes=[("SVG files", "*.svg"),
                                                                   ("All files", "*.*")])
        if svg_output_path:
            try:
                # Call the save_as_svg function with the selected path
                background_path = './temp/bg.png'
                product_path = './temp/product-nonbg.png'
                # Save the SVG using the existing function
                save_as_svg(Image.open(background_path), Image.open(product_path), self.slogan, svg_output_path)
                tk.messagebox.showinfo("Success", f"SVG saved successfully at: {svg_output_path}")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to save SVG: {e}")

    def open_boxy_svg(self):
        """Open Boxy SVG in the default web browser"""
        webbrowser.open("https://boxy-svg.com/")

    def finish_app(self):
        """Close the application, copy temp folder contents to future_dataset, and save product details to a text file."""
        # Define the source and destination paths
        temp_folder = './temp'
        future_dataset_folder = './future_dataset'
        
        # Create a new folder name based on the current date and time
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        new_folder_path = os.path.join(future_dataset_folder, current_time)

        # Create the new folder if it doesn't exist
        os.makedirs(new_folder_path, exist_ok=True)

        # Copy contents from temp folder to the new folder
        try:
            for item in os.listdir(temp_folder):
                s = os.path.join(temp_folder, item)
                d = os.path.join(new_folder_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, False, None)  # Copy directory
                else:
                    shutil.copy2(s, d)  # Copy file
            tk.messagebox.showinfo("Success", f"Files copied to: {new_folder_path}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to copy files: {e}")

        # Save product details to a text file
        details_file_path = os.path.join(new_folder_path, "product_details.txt")
        try:
            with open(details_file_path, 'w') as f:
                f.write(f"Product Name: {self.product_name}\n")
                f.write(f"Product Description: {self.description}\n")
                f.write(f"Slogan Generated: {self.slogan}\n")
                f.write(f"Caption Generated: {self.caption}\n")
            tk.messagebox.showinfo("Success", f"Product details saved to: {details_file_path}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to save product details: {e}")

        self.root.destroy()  # Close the Tkinter window

    def create_final_image(self, text_color="white"):  # Set default to white
        """Create and display the final image"""
        # Load images from the temp folder
        background_path = './temp/bg.png'
        product_path = './temp/product-nonbg.png'
        final_image_path = './temp/final_image.png'  # Path to save the final image
        svg_output_path = './temp/final_image.svg'  # Path to save the SVG file

        # Use self.text_color if it's set, otherwise default to white
        if self.text_color is None:
            text_color = "white"
        else:
            text_color = self.text_color
        
        # Print the text color being used
        print(f"Text color being used: {text_color}")

        try:
            # Load the background and product images
            background_image = Image.open(background_path)
            product_image = Image.open(product_path)

            # Create the final image
            final_image = create_final_image(background_image, product_image, self.slogan, text_color)

            # Save the final image as PNG
            final_image.save(final_image_path, format="PNG")
            print(f"Final image created and saved as '{final_image_path}'.")

            # Save the final image as a layered SVG
            save_as_svg(background_image, product_image, self.slogan, svg_output_path)
            print(f"SVG file created and saved as '{svg_output_path}'.")

            return final_image_path  # Return the path of the saved image

        except Exception as e:
            print(f"Error processing images: {e}")
            return None  # Return None in case of error

    def update_page_number(self, page_number):
        """Force update the page number"""
        self.page_label.config(text=f"Page {page_number} of 6")

    def generate_slogan_with_loading(self):
        """Generate slogan with loading animation"""
        # Show loading spinner
        self.slogan_loading.pack(pady=5)
        self.slogan_loading.start(10)
        
        # Disable the generate button during processing
        for widget in self.display_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.DISABLED)
        
        # Process in background thread
        thread = threading.Thread(target=self._process_slogan_generation)
        thread.start()

    def _process_slogan_generation(self):
        """Process slogan generation in background thread"""
        try:
            new_slogan = self.generate_slogan()
            # Schedule UI update on main thread
            self.root.after(0, self._finish_slogan_generation, new_slogan)
        except Exception as e:
            print(f"Error in slogan generation: {e}")
            self.root.after(0, self._handle_slogan_generation_error)

    def _finish_slogan_generation(self, new_slogan):
        """Update UI after slogan generation is complete"""
        # Remove loading spinner
        self.slogan_loading.stop()
        self.slogan_loading.pack_forget()
        
        # Re-enable buttons
        for widget in self.display_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.NORMAL)
        
        # Update the text widget with new slogan
        self.slogan_text.delete(1.0, tk.END)
        self.slogan_text.insert(1.0, new_slogan)

    def _handle_slogan_generation_error(self):
        """Handle errors in slogan generation"""
        # Remove loading spinner
        self.slogan_loading.stop()
        self.slogan_loading.pack_forget()
        
        # Re-enable buttons
        for widget in self.display_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.NORMAL)
        
        # Show error message
        self.slogan_text.delete(1.0, tk.END)
        self.slogan_text.insert(1.0, "Error generating slogan. Please try again.")

    def show_loading(self, message="Loading..."):
        """Display a loading message"""
        self.loading_label = ttk.Label(self.root, text=message, font=("Helvetica", 12))
        self.loading_label.pack(pady=10)

    def hide_loading(self):
        """Hide the loading message"""
        if hasattr(self, 'loading_label'):
            self.loading_label.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductApp(root)
    root.mainloop()
