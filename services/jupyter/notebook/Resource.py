import requests
import weaviate
import io
import os
import pdf2image

class Resource:
    def __init__(self, path):
        extension = os.path.splitext(path)[1]
        if extension == ".pdf":
            self.images = pdf2image.convert_from_path(path)

    def read(self):
        assert("images" in self.__dict__)
        self.text = ""
        
        for image in self.images:
            # Convert image to bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="JPEG")
            img_bytes.seek(0)  # Reset the pointer to the beginning of the byte stream

            # Send image to OCR service and get the text
            response = requests.post(
                "http://ocr/read",
                files= {
                    "file": img_bytes
                }
            )
            self.text += response.json().get("text", "") + "\n"
