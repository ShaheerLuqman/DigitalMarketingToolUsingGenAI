import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import shutil
from rembg import remove
import threading
from tkinter import ttk

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
        
        self.page_label = tk.Label(self.page_indicator_frame, text="Page 1 of 3", font=("Helvetica", 12))
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
        self.page_label.config(text="Page 2 of 3")

        # Enable Next button when moving to background removal page
        self.next_button.config(state=tk.NORMAL, command=self.remove_background)

    def go_back(self):
        """Go back to the previous page"""
        if self.processed_image_path:  # If on page 3
            self.processed_image_path = None
            self.display_product_info()  # Go back to page 2
        else:  # If on page 2
            self.display_frame.pack_forget()
            self.form_frame.pack(pady=10)
            self.title_label.config(text="Product Information")
            self.back_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.NORMAL)
            self.page_label.config(text="Page 1 of 3")

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
        output_img.save(output_path)
        
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
        self.next_button.config(state=tk.DISABLED)
        self.back_button.config(state=tk.NORMAL)

        # Update page indicator
        self.page_label.config(text="Page 3 of 3")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductApp(root)
    root.mainloop()
