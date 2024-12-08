import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import shutil
from rembg import remove
import threading
from tkinter import ttk
from bg_generator import process_product_image

class ProductApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Info App")

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set window size and position it 100px below the top
        self.root.geometry(f"1600x900+{int((screen_width - 1600) / 2)}+50")

        # Initialize variables
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
            process_product_image(product_image, output_path)
            
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
        """Placeholder function to generate slogan"""
        return "Amazing Product - Buy Now!"

    def generate_caption(self):
        """Placeholder function to generate caption"""
        return "Experience the incredible features of our latest product. #amazing #product"

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

        # Create slogan button and text box
        generate_slogan_btn = tk.Button(
            slogan_frame,
            text="Generate Slogan",
            font=("Helvetica", 14),
            command=lambda: slogan_text.insert(1.0, self.generate_slogan())
        )
        generate_slogan_btn.pack(pady=(0, 10))

        slogan_text = tk.Text(slogan_frame, height=3, width=50, font=("Helvetica", 12))
        slogan_text.pack()
        if self.slogan:
            slogan_text.insert(1.0, self.slogan)

        # Create frame for caption section
        caption_frame = tk.Frame(self.display_frame)
        caption_frame.pack(pady=20, fill=tk.X, padx=20)

        # Create caption button and text box
        generate_caption_btn = tk.Button(
            caption_frame,
            text="Generate Caption",
            font=("Helvetica", 14),
            command=lambda: caption_text.insert(1.0, self.generate_caption())
        )
        generate_caption_btn.pack(pady=(0, 10))

        caption_text = tk.Text(caption_frame, height=5, width=50, font=("Helvetica", 12))
        caption_text.pack()
        if self.caption:
            caption_text.insert(1.0, self.caption)

        # Store text widgets references for accessing their content later
        self.slogan_text = slogan_text
        self.caption_text = caption_text

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

        # Display the post
        self.display_post()

        # Update button states
        self.next_button.config(state=tk.DISABLED)  # Disable next since it's the last page
        self.back_button.config(state=tk.NORMAL)

        # Update page indicator
        self.update_page_number(6)

    def display_post(self):
        """Display the generated post"""
        # Get SVG path from generate function
        svg_path = self.generate_post()
        
        if os.path.exists(svg_path):
            try:
                # Convert SVG to PNG for display
                from cairosvg import svg2png
                import io
                
                # Read SVG file
                with open(svg_path, 'rb') as svg_file:
                    svg_data = svg_file.read()
                
                # Convert to PNG
                png_data = svg2png(bytestring=svg_data)
                
                # Create PIL Image from PNG data
                img = Image.open(io.BytesIO(png_data))
                img.thumbnail((700, 700))
                photo = ImageTk.PhotoImage(img)
                
                # Display the image
                img_label = tk.Label(self.display_frame, image=photo)
                img_label.image = photo
                img_label.pack(pady=20)
                
            except Exception as e:
                print(f"Error displaying post: {e}")
                error_label = tk.Label(
                    self.display_frame,
                    text="Error displaying the post",
                    font=("Helvetica", 14),
                    fg="red"
                )
                error_label.pack(pady=20)

    def update_page_number(self, page_number):
        """Force update the page number"""
        self.page_label.config(text=f"Page {page_number} of 6")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductApp(root)
    root.mainloop()
