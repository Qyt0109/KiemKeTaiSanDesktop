import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout
import qrcode

class QRCodeGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Create widgets
        self.label = QLabel('Enter text:')
        self.text_input = QLineEdit()
        self.generate_button = QPushButton('Generate QR Code')
        self.generate_button.clicked.connect(self.generate_qr_code)
        
        # Set up the layout
        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.text_input)
        layout.addWidget(self.generate_button)

        # Set up the main window
        self.setWindowTitle('QR Code Generator')
        self.setGeometry(100, 100, 400, 200)

    def generate_qr_code(self):
        data = self.text_input.text()

        if not data:
            return  # Do nothing if the input is empty

        # Open a file dialog to get the save path
        file_dialog = QFileDialog(self)
        file_dialog.setDefaultSuffix('png')
        file_path, _ = file_dialog.getSaveFileName(self, 'Save QR Code As', '', 'Images (*.png)')

        if file_path:
            self.save_qr_code(data, file_path)

    def save_qr_code(self, data, file_path):
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=2,
        )
        
        # Add data to the QR code
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QR code instance
        img = qr.make_image(fill_color="black", back_color="white")

        # Save the image to a file
        img.save(file_path)
        

def main():
    app = QApplication(sys.argv)
    window = QRCodeGeneratorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
