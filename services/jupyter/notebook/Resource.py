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
                files = {
                    "file": img_bytes
                }
            )
            self.text += response.json().get("text") + "\n"

    def split(self, lang = "en"):
        assert("text" in self.__dict__)

        # Send text to tokenizer service and get the chunks
        response = requests.post(
            "http://tokenizer/split",
            json = {
                "text": self.text,
                "lang": lang,
            }
        )
        self.sentences = response.json().get("sentences")

    def vectorize(self):
        assert("sentences" in self.__dict__)

        # Send text to tokenizer service and get the chunks
        response = requests.post(
            "http://encoder/v1/vectorize",
            json = {
                "text": self.sentences,
            }
        )
        self.vectors = response.json()
        
    def store(self):
        pass



