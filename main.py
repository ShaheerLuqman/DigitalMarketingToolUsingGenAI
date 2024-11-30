import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

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

        # Title
        self.title_label = tk.Label(self.root, text="Product Information", font=("Helvetica", 24))
        self.title_label.pack(pady=20)

        # Form frame
        self.form_frame = tk.Frame(self.root)
        self.form_frame.pack(pady=10)

        # Description Label and Textbox
        self.description_label = tk.Label(self.form_frame, text="Enter product description:", font=("Helvetica", 14))
        self.description_label.pack(pady=5)

        self.description_entry = tk.Entry(self.form_frame, width=50, font=("Helvetica", 14))
        self.description_entry.pack(pady=5)

        # Upload Image Button
        self.upload_button = tk.Button(self.form_frame, text="Upload Product Image", font=("Helvetica", 14), command=self.upload_image)
        self.upload_button.pack(pady=10)

        # Image thumbnail label (initially None)
        self.thumbnail_label = None

        # Display Area (initially hidden)
        self.display_frame = tk.Frame(self.root)

        # Image and description labels (initially set to None)
        self.img_label = None
        self.desc_label = None
        self.back_button = None  # Initialize the back button here

        # Bottom Button Frame for Back and Next buttons
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        # Back Button (Initially disabled)
        self.back_button = tk.Button(self.bottom_frame, text="Back", font=("Helvetica", 14), state=tk.DISABLED, command=self.go_back)
        self.back_button.pack(side=tk.LEFT, padx=20)

        # Next Button (Initially enabled)
        self.next_button = tk.Button(self.bottom_frame, text="Next", font=("Helvetica", 14), state=tk.DISABLED, command=self.display_product_info)
        self.next_button.pack(side=tk.RIGHT, padx=20)

    def upload_image(self):
        """Upload image file"""
        # Ask the user to select a new image
        new_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

        if new_image_path:
            # Only update the image if a new image is selected
            if new_image_path != self.image_path:  # Check if the new image is different from the previous one
                self.image_path = new_image_path

                # Remove previous thumbnail if it exists
                if self.thumbnail_label:
                    self.thumbnail_label.pack_forget()  # Remove the old thumbnail
                    self.root.update_idletasks()  # Force the display to refresh

                # Create and display the new thumbnail
                img = Image.open(self.image_path)
                img.thumbnail((100, 100))  # Create a thumbnail (100x100)
                img = ImageTk.PhotoImage(img)

                # Create a new label for the thumbnail
                self.thumbnail_label = tk.Label(self.form_frame, image=img)
                self.thumbnail_label.image = img  # Keep a reference to the image object
                self.thumbnail_label.pack(pady=10)

                # Enable the Next button after image upload
                self.next_button.config(state=tk.NORMAL)

    def display_product_info(self):
        """Display the product image and description"""
        self.description = self.description_entry.get()

        if not self.image_path or not self.description:
            tk.messagebox.showerror("Error", "Please provide both image and description!")
            return

        # Hide form and show display frame
        self.form_frame.pack_forget()
        self.display_frame.pack(pady=20)

        # Disable the Next button and enable the Back button after moving to display
        self.next_button.config(state=tk.DISABLED)
        self.back_button.config(state=tk.NORMAL)

        # Create a frame for image display to ensure layout is clean
        image_frame = tk.Frame(self.display_frame)
        image_frame.pack(pady=20)

        # If the labels are already created, just update them
        if not self.img_label or not self.desc_label:
            # Load and display the image
            img = Image.open(self.image_path)
            img.thumbnail((700, 700))  # Resize the image to fit within the 700x700 box
            img = ImageTk.PhotoImage(img)

            self.img_label = tk.Label(image_frame, image=img)
            self.img_label.image = img  # Keep a reference to the image object
            self.img_label.pack()

            # Display the description below the image
            self.desc_label = tk.Label(self.display_frame, text="Description: " + self.description, font=("Helvetica", 14), wraplength=1200)
            self.desc_label.pack(pady=10)

        else:
            # Update the existing image and description labels
            img = Image.open(self.image_path)
            img.thumbnail((700, 700))  # Resize the image to fit within the 700x700 box
            img = ImageTk.PhotoImage(img)
            self.img_label.config(image=img)
            self.img_label.image = img  # Update the image reference

            self.desc_label.config(text="Description: " + self.description)  # Update the description text

        # Disable Next button and keep Back button enabled when on the last page
        self.next_button.config(state=tk.DISABLED)

    def go_back(self):
        """Go back to the input form"""
        self.display_frame.pack_forget()
        self.form_frame.pack(pady=10)

        # Disable Back button and enable Next button on the first page
        self.back_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductApp(root)
    root.mainloop()
