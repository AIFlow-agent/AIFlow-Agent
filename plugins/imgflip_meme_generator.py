import requests

from utils.logging_utils import enable_logging, log_message, setup_logging

logger = setup_logging()
logging_enabled = True
enable_logging(logging_enabled)


class ImgflipMemeGenerator:
    def __init__(self, imgflip_username, imgflip_password):
        self.imgflip_username = imgflip_username
        self.imgflip_password = imgflip_password

    def generate_automeme(self, text, no_watermark=False):
        url = "https://api.imgflip.com/automeme"

        payload = {
            "username": self.imgflip_username,
            "password": self.imgflip_password,
            "text": text,
            "no_watermark": no_watermark,
        }

        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    return result["data"]["url"]
                else:
                    raise Exception(f"Error: {result['error_message']}")
            else:
                raise Exception(f"HTTP Error: {response.status_code}")

        except Exception as e:
            log_message(logger, "error", self, f"Error generating a meme: {e}")
            return None

    def generate_ai_meme(
        self, model="openai", template_id=None, prefix_text=None, no_watermark=False
    ):
        url = "https://api.imgflip.com/ai_meme"
        payload = {
            "username": self.imgflip_username,
            "password": self.imgflip_password,
            "model": model,
            "prefix_text": prefix_text,
            "no_watermark": no_watermark,
        }
        if template_id:
            payload["template_id"] = template_id
        if prefix_text:
            payload["prefix_text"] = prefix_text

        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    return result["data"]["url"]
                else:
                    raise Exception(f"Error: {result['error_message']}")
            else:
                raise Exception(f"HTTP Error: {response.status_code}")
        except Exception as e:
            log_message(logger, "error", self, f"Error generating an AI meme: {e}")
            return None
