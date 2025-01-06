from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
import requests

from utils.logging_utils import enable_logging, log_message, setup_logging

logger = setup_logging()
enable_logging(True)


def save_image_from_url(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
        print(f"Image saved successfully at {save_path}")
        return save_path
    else:
        print(f"Failed to retrieve image from URL: {image_url}")


def generate_image_dalle(input_prompt):
    try:
        image_url = DallEAPIWrapper().run(input_prompt)
        log_message(
            logger,
            "info",
            generate_image_dalle,
            f"Generated image with DALL-E: {image_url}",
        )
        return image_url
    except Exception as e:
        log_message(
            logger,
            "error",
            generate_image_dalle,
            f"Error generating image with DALL-E: {e}",
        )
        return None
