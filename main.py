from PIL import Image, ImageDraw
from pathlib import Path
import numpy as np
import keyboard
import pyautogui
import tkinter as tk
from datetime import datetime
import tkinter.ttk as ttk
import re
import sys

def create_rounded_snippet(input_path, output_path, corner_radius=20,
                         gradient_colors=((135, 206, 235), (147, 112, 219)),
                         padding=50, shadow=0, balance=False, redact_emails=False):
    # Open the original screenshot
    original = Image.open(input_path)
    
    # Create a new image with padding for the gradient background
    new_width = original.width + (padding * 2)
    new_height = original.height + (padding * 2)
    
    # Create gradient background
    background = Image.new('RGBA', (new_width, new_height))
    draw = ImageDraw.Draw(background)
    
    # Create gradient
    if gradient_colors:
        for y in range(new_height):
            ratio = y / new_height
            r = int(gradient_colors[0][0] * (1 - ratio) + gradient_colors[1][0] * ratio)
            g = int(gradient_colors[0][1] * (1 - ratio) + gradient_colors[1][1] * ratio)
            b = int(gradient_colors[0][2] * (1 - ratio) + gradient_colors[1][2] * ratio)
            draw.line([(0, y), (new_width, y)], fill=(r, g, b, 255))
    else:
        background = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    
    # Improved shadow effect
    if shadow > 0:
        shadow_img = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        
        # Create multiple layers of shadow for a softer effect
        max_layers = 15
        base_opacity = 120
        spread = shadow * 0.7  # Controls shadow spread
        
        for i in range(max_layers):
            # Calculate decreasing opacity for each layer
            opacity = int(base_opacity * (1 - i/max_layers))
            offset = i * (spread/max_layers)
            
            # Draw shadow layer with rounded corners
            shadow_draw.rounded_rectangle(
                [(padding + offset, padding + offset),
                 (new_width - padding + offset, new_height - padding + offset)],
                corner_radius,
                fill=(0, 0, 0, opacity)
            )
        
        # Apply Gaussian-like blur to the shadow
        from PIL import ImageFilter
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=shadow/4))
        background = Image.alpha_composite(background, shadow_img)
    
    # Create mask for rounded corners
    mask = Image.new('L', (original.width, original.height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (original.width-1, original.height-1)], 
                              corner_radius, fill=255)
    
    # Improved email redaction
    if redact_emails:
        try:
            import easyocr
            from PIL import ImageEnhance

            # Prepare image for better OCR
            ocr_image = original.copy()
            
            # Enhance image for better text detection
            enhancer = ImageEnhance.Contrast(ocr_image)
            ocr_image = enhancer.enhance(1.5)
            enhancer = ImageEnhance.Sharpness(ocr_image)
            ocr_image = enhancer.enhance(1.5)

            # Initialize EasyOCR with multiple languages for better detection
            reader = easyocr.Reader(['en'])
            
            # Read text from image
            results = reader.readtext(np.array(ocr_image))
            
            # Find and redact emails
            if results:
                draw = ImageDraw.Draw(original)
                redacted_count = 0
                
                for bbox, text, conf in results:
                    # Only check lines containing '@'
                    if '@' in text:
                        # Standard email pattern
                        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                        if re.search(email_pattern, text):
                            # Convert points to rectangle
                            points = np.array(bbox).astype(np.int32)
                            x1, y1 = points.min(axis=0)
                            x2, y2 = points.max(axis=0)
                            
                            # Add padding to redaction
                            padding_x = int((x2 - x1) * 0.1)
                            padding_y = int((y2 - y1) * 0.1)
                            x1 = max(0, x1 - padding_x)
                            y1 = max(0, y1 - padding_y)
                            x2 = min(original.width, x2 + padding_x)
                            y2 = min(original.height, y2 + padding_y)
                            
                            # Draw black rectangle over email
                            draw.rectangle([x1, y1, x2, y2], fill='black')
                            redacted_count += 1
                
                # Update checkbox text with count if available
                if 'redact_checkbox' in globals():
                    redact_checkbox.configure(
                        text=f"Redact email addresses (found {redacted_count})"
                    )

        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showwarning(
                "Email Redaction Not Available",
                "To use email redaction, please install EasyOCR:\n\n"
                "pip install easyocr\n\n"
                "Note: First use may require downloading model files."
            )
            if 'redact_var' in globals():
                redact_var.set(False)
    
    # Apply mask to original image
    output = Image.new('RGBA', (original.width, original.height), (0, 0, 0, 0))
    output.paste(original, mask=mask)
    
    # Apply balance if requested
    if balance:
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(output)
        output = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Brightness(output)
        output = enhancer.enhance(1.1)
    
    # Paste the final image onto the background
    background.paste(output, (padding, padding), output)
    
    # Add watermark if requested
    if hasattr(create_rounded_snippet, 'watermark') and create_rounded_snippet.watermark:
        watermark = Image.new('RGBA', (new_width, 30), (0, 0, 0, 0))
        watermark_draw = ImageDraw.Draw(watermark)
        watermark_draw.text((new_width-100, 5), "Ralph-o-snapic", fill=(0, 0, 0, 128))
        background.paste(watermark, (0, new_height-30), watermark)
    
    # Save the final image
    background.save(output_path, 'PNG')

def show_settings(screenshot_path, final_path):
    # Create settings window
    settings = tk.Tk()
    settings.title("Ralph's xnapper copy but opensource")
    settings.configure(bg='#f5f5f5')  # Light background
    
    # Configure styles
    style = ttk.Style()
    style.configure('Modern.TFrame', background='#f5f5f5')
    style.configure('Modern.TLabel', 
                   background='#f5f5f5', 
                   font=('Segoe UI', 13))
    style.configure('Modern.TRadiobutton', 
                   background='#f5f5f5', 
                   font=('Segoe UI', 11))
    style.configure('Modern.Horizontal.TScale', background='#f5f5f5')
    style.configure('Modern.TCheckbutton', 
                   background='#f5f5f5',
                   font=('Segoe UI', 11))
    style.configure('Modern.TButton',
                   font=('Segoe UI', 11),
                   padding=10)
    
    # Main layout
    main_frame = ttk.Frame(settings, style='Modern.TFrame')
    main_frame.pack(padx=20, pady=20, expand=True, fill='both')
    
    # Left side - Preview
    preview_frame = ttk.Frame(main_frame, style='Modern.TFrame')
    preview_frame.pack(side='left', padx=20)
    
    # Create preview label early
    preview_label = ttk.Label(preview_frame, style='Modern.TLabel')
    preview_label.pack()
    
    def update_preview(*args):
        try:
            # Create temporary file for preview
            preview_path = "temp_preview.png"
            
            # Create the processed image with current settings
            create_rounded_snippet(
                screenshot_path,
                preview_path,
                corner_radius=radius_var.get(),
                gradient_colors=presets[preset_var.get()] if preset_var.get() != 'None' else None,
                padding=padding_var.get(),
                shadow=shadow_var.get(),
                balance=balance_var.get(),
                redact_emails=redact_var.get()
            )
            
            # Update watermark setting
            create_rounded_snippet.watermark = watermark_var.get()
            
            # Load and display preview image
            img = Image.open(preview_path)
            
            # Scale image if too large
            max_size = (600, 400)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(preview_path)
            
            # Update the preview image
            settings.preview_image = tk.PhotoImage(file=preview_path)
            preview_label.configure(image=settings.preview_image)
            
            # Clean up temporary file
            Path(preview_path).unlink()
        except Exception as e:
            print(f"Preview error: {e}")
    
    # Right side - Settings
    settings_frame = ttk.Frame(main_frame, style='Modern.TFrame')
    settings_frame.pack(side='right', padx=20, fill='y')
    
    # Padding control
    ttk.Label(settings_frame, text="Padding", 
             style='Modern.TLabel').pack(anchor='w', pady=(0,5))
    padding_var = tk.IntVar(value=50)
    padding_slider = ttk.Scale(settings_frame, from_=0, to=100, 
                             orient='horizontal',
                             variable=padding_var,
                             command=update_preview)
    padding_slider.pack(fill='x', pady=(0,20))
    
    balance_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(settings_frame, text="Balance",
                    variable=balance_var,
                    style='Modern.TCheckbutton',
                    command=update_preview).pack(anchor='e')
    
    # Border and Shadow controls
    control_frame = ttk.Frame(settings_frame, style='Modern.TFrame')
    control_frame.pack(fill='x', pady=(0,20))
    
    # Border Radius
    border_frame = ttk.Frame(control_frame, style='Modern.TFrame')
    border_frame.pack(side='left', fill='x', expand=True)
    ttk.Label(border_frame, text="Border Radius",
             style='Modern.TLabel').pack(anchor='w')
    radius_var = tk.IntVar(value=20)
    radius_slider = ttk.Scale(border_frame, from_=0, to=40,
                            orient='horizontal',
                            variable=radius_var,
                            command=update_preview)
    radius_slider.pack(fill='x', padx=(0,10))
    
    # Shadow
    shadow_frame = ttk.Frame(control_frame, style='Modern.TFrame')
    shadow_frame.pack(side='right', fill='x', expand=True)
    ttk.Label(shadow_frame, text="Shadow",
             style='Modern.TLabel').pack(anchor='w')
    shadow_var = tk.IntVar(value=0)
    shadow_slider = ttk.Scale(shadow_frame, from_=0, to=40,
                            orient='horizontal',
                            variable=shadow_var,
                            command=update_preview)
    shadow_slider.pack(fill='x')
    
    # Background presets
    ttk.Label(settings_frame, text="Background",
             style='Modern.TLabel').pack(anchor='w', pady=(0,10))
    
    presets = {
        'Desktop': ((255, 140, 0), (255, 98, 0)),     # Orange gradient
        'Cool': ((135, 206, 235), (147, 112, 219)),   # Sky Blue to Purple
        'Nice': ((255, 192, 203), (147, 112, 219)),   # Pink to Purple
        'Morning': ((255, 182, 193), (255, 218, 185)), # Light Pink to Peach
        'Bright': ((255, 140, 0), (138, 43, 226)),    # Orange to Purple
        'Love': ((255, 105, 180), (138, 43, 226)),    # Hot Pink to Purple
        'Rain': ((0, 191, 255), (138, 43, 226)),      # Deep Sky Blue to Purple
        'Sky': ((135, 206, 235), (70, 130, 180)),     # Sky Blue to Steel Blue
        'None': None,                                  # No gradient
        'Custom': None                                 # Custom gradient
    }
    
    # Create grid of preset buttons
    preset_frame = ttk.Frame(settings_frame, style='Modern.TFrame')
    preset_frame.pack(fill='x', pady=(0,20))
    
    preset_var = tk.StringVar(value='Cool')
    row = 0
    col = 0
    for preset in presets:
        btn = ttk.Radiobutton(preset_frame, text=preset,
                             variable=preset_var,
                             value=preset,
                             style='Modern.TRadiobutton',
                             command=update_preview)
        btn.grid(row=row, column=col, padx=5, pady=2, sticky='w')
        col += 1
        if col > 4:  # 5 columns
            col = 0
            row += 1
    
    # Check if EasyOCR is available
    easyocr_available = False
    try:
        import easyocr
        easyocr_available = True
    except ImportError:
        pass

    # Additional options
    redact_var = tk.BooleanVar(value=False)
    redact_checkbox = ttk.Checkbutton(
        settings_frame, 
        text="Redact email addresses" + (" (EasyOCR not installed)" if not easyocr_available else ""),
        variable=redact_var,
        style='Modern.TCheckbutton',
        command=update_preview,
        state='normal' if easyocr_available else 'disabled'
    )
    redact_checkbox.pack(anchor='w', pady=2)
    
    watermark_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(settings_frame, text="Show watermark",
                    variable=watermark_var,
                    style='Modern.TCheckbutton',
                    command=update_preview).pack(anchor='w', pady=2)
    
    # Add Apply button at the bottom of settings_frame
    def apply_settings():
        try:
            # Create final image
            create_rounded_snippet(
                screenshot_path,
                final_path,
                corner_radius=radius_var.get(),
                gradient_colors=presets[preset_var.get()] if preset_var.get() != 'None' else None,
                padding=padding_var.get(),
                shadow=shadow_var.get(),
                balance=balance_var.get(),
                redact_emails=redact_var.get()
            )
            
            # Copy to clipboard
            try:
                from PIL import ImageGrab
                import win32clipboard
                from io import BytesIO
                
                # Convert image to BMP format for clipboard
                image = Image.open(final_path)
                output = BytesIO()
                image.convert('RGB').save(output, 'BMP')
                data = output.getvalue()[14:]  # Remove BMP header
                output.close()
                
                # Send to clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
            except Exception as e:
                print(f"Clipboard error: {e}")
                # Try alternative method for non-Windows systems
                try:
                    import subprocess
                    if sys.platform == 'darwin':  # macOS
                        subprocess.run(['osascript', '-e', 
                            f'set the clipboard to (read (POSIX file "{final_path}") as JPEG picture)'])
                    elif sys.platform.startswith('linux'):  # Linux
                        subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', final_path])
                except Exception as e:
                    print(f"Alternative clipboard method error: {e}")
            
            # Close the settings window
            settings.destroy()
            
        except Exception as e:
            print(f"Apply error: {e}")

    # Create Apply button with modern style
    apply_button = ttk.Button(
        settings_frame,
        text="Apply",
        command=apply_settings,
        style='Modern.TButton'
    )
    apply_button.pack(pady=20)

    # Create initial preview
    update_preview()
    
    # Center the window on screen
    settings.update_idletasks()
    width = settings.winfo_width()
    height = settings.winfo_height()
    x = (settings.winfo_screenwidth() // 2) - (width // 2)
    y = (settings.winfo_screenheight() // 2) - (height // 2)
    settings.geometry(f'+{x}+{y}')
    
    settings.mainloop()

def take_screenshot():
    # Create a transparent root window
    root = tk.Tk()
    root.attributes('-alpha', 0.1)
    root.attributes('-fullscreen', True)
    
    # Create a canvas for drawing the selection rectangle
    canvas = tk.Canvas(root, highlightthickness=0)
    canvas.pack(fill='both', expand=True)
    canvas.configure(cursor="cross")
    
    # Create magnifier window
    magnifier = tk.Toplevel(root)
    magnifier.overrideredirect(True)
    magnifier.attributes('-topmost', True)
    mag_size = 120  # Size of magnifier window
    mag_canvas = tk.Canvas(magnifier, width=mag_size, height=mag_size)
    mag_canvas.pack()
    
    # Variables to store coordinates
    start_x = start_y = 0
    selection_rect = None
    
    def update_magnifier(event):
        try:
            # Get screen content around cursor
            x, y = event.x_root, event.y_root
            screenshot = pyautogui.screenshot(region=(x-10, y-10, 20, 20))
            # Scale up the screenshot for magnifier
            screenshot = screenshot.resize((mag_size, mag_size))
            # Save and load as PNG instead of using PPM
            temp_path = "temp_mag.png"
            screenshot.save(temp_path)
            photo = tk.PhotoImage(file=temp_path)
            mag_canvas.delete("all")
            mag_canvas.create_image(0, 0, image=photo, anchor="nw")
            mag_canvas.image = photo  # Keep a reference
            # Clean up temp file
            Path(temp_path).unlink()
            # Draw crosshair
            mag_canvas.create_line(mag_size/2, 0, mag_size/2, mag_size, fill='red')
            mag_canvas.create_line(0, mag_size/2, mag_size, mag_size/2, fill='red')
            # Position magnifier window near cursor but not under it
            offset_x = 10
            offset_y = 10
            magnifier.geometry(f"{mag_size}x{mag_size}+{x+offset_x}+{y+offset_y}")
        except Exception as e:
            print(f"Magnifier error: {e}")
    
    def on_mouse_down(event):
        nonlocal start_x, start_y
        start_x, start_y = event.x, event.y
        magnifier.deiconify()  # Show magnifier
        update_magnifier(event)
        
    def on_mouse_move(event):
        nonlocal selection_rect
        if event.state & 0x0100:  # Check if left mouse button is held down
            # Remove previous rectangle
            if selection_rect:
                canvas.delete(selection_rect)
            # Draw new rectangle
            selection_rect = canvas.create_rectangle(
                start_x, start_y, event.x, event.y,
                outline='#0078D7',  # Windows blue color
                width=2
            )
            update_magnifier(event)
    
    def on_mouse_up(event):
        end_x, end_y = event.x, event.y
        # Clean up visual elements
        if selection_rect:
            canvas.delete(selection_rect)
        magnifier.withdraw()  # Hide magnifier
        root.quit()
        
        # Ensure coordinates are in the correct order
        left = min(start_x, end_x)
        top = min(start_y, end_y)
        width = abs(end_x - start_x)
        height = abs(end_y - start_y)
        
        # Take the screenshot of selected area
        if width > 0 and height > 0:
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # Create output directory if it doesn't exist
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            input_path = output_dir / f"screenshot_{timestamp}.png"
            output_path = output_dir / f"processed_{timestamp}.png"
            
            # Save original screenshot
            screenshot.save(input_path)
            
            # Ensure windows are destroyed
            try:
                magnifier.destroy()
                root.destroy()
            except:
                pass
            
            # Show settings window
            show_settings(input_path, output_path)
            
            # Clean up original screenshot
            input_path.unlink()
    
    # Bind mouse events
    canvas.bind('<Button-1>', on_mouse_down)
    canvas.bind('<B1-Motion>', on_mouse_move)
    canvas.bind('<ButtonRelease-1>', on_mouse_up)
    
    # Add escape key to cancel
    def on_escape(event):
        magnifier.withdraw()
        root.destroy()
    root.bind('<Escape>', on_escape)
    
    # Initially hide magnifier
    magnifier.withdraw()
    
    # Start the selection process
    root.mainloop()
    
    # Ensure windows are destroyed
    try:
        root.destroy()
        magnifier.destroy()
    except:
        pass

def on_hotkey():
    take_screenshot()

# Register the hotkey
keyboard.add_hotkey('ctrl+shift+q', on_hotkey)

# Example usage
if __name__ == "__main__":
    print("Press Ctrl+Shift+Q to take a screenshot. Press Ctrl+C to exit.")
    # Keep the program running
    keyboard.wait('ctrl+c')
