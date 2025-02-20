# wnapper

![wnapper Logo](img/logo.png) <!-- Replace with your logo path -->

wnapper is a powerful and user-friendly screenshot tool that allows you to capture, edit, and enhance your screenshots with ease. With features like rounded corners, gradient backgrounds, email redaction, and more, wnapper is designed to help you create stunning visuals quickly.

## Features

- **Capture Screenshots**: Easily take screenshots of your screen or selected areas.
- **Edit and Enhance**: Apply rounded corners, shadows, and gradient backgrounds to your images.
- **Email Redaction**: Automatically redact email addresses from your screenshots using EasyOCR.
- **Customizable Settings**: Adjust padding, border radius, shadow intensity, and more.
- **Clipboard Support**: Copy your processed images directly to the clipboard for easy sharing.

## Installation

To get started with wnapper, clone the repository and install the required packages:
```bash
git clone https://github.com/foxdatasystems/wnapper.git
cd wnapper
pip install -r requirements.txt
```

### Requirements

- Python 3.x
- Tesseract OCR (for email redaction)
- EasyOCR

## Usage

1. Run the application:
   ```bash
   python wnapper.py
   ```
2. Use the hotkey `Ctrl + Shift + Q` to take a screenshot.
3. Adjust the settings in the GUI to customize your screenshot.
4. Click the "Apply" button to process the image and copy it to your clipboard.

## Screenshots

![Screenshot Example](img/example.png) <!-- Replace with your screenshot path -->

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for text recognition.
- [Pillow](https://python-pillow.org/) for image processing.
- [Tkinter](https://wiki.python.org/moin/TkInter) for GUI development.
- [Keyboard](https://keyboard.readthedocs.io/en/latest/) for hotkey functionality.
- [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/) for GUI automation.
