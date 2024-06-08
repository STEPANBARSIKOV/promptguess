import json
import time
from config import *
import requests
import base64
from PIL import Image
from io import BytesIO
import openai
import random

class Text2ImageAPI:
    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)

    def convert_to_img(self, base64_string, path):
        decoded_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(decoded_data))
        image.save(path)

class OpenAIAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key

    def generate_prompts(self, initial_prompt, num_prompts=4):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Generate {num_prompts} different image prompts based on this prompt: {initial_prompt}"}
            ],
            n=num_prompts,
            temperature=0.7
        )
        prompts = [choice['message']['content'].strip() for choice in response.choices]
        return prompts

if __name__ == '__main__':
    initial_prompt = "Generate 4 creative image prompts"
    ai = OpenAIAPI(GPT_KEY)
    prompts = ai.generate_prompts(initial_prompt)
    print(prompts)
