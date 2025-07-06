from flask import Flask, request, render_template, jsonify
from PIL import Image
import numpy as np
import io
import pickle
import tensorflow as tf
import base64
import requests

app = Flask(__name__)

# Load the Generator model
with open('Generator_1.pkl', 'rb') as file:
    generator_model = pickle.load(file)

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
headers = {"Authorization": "Hugging Face Token"}

# Define the normalization function
def Normalize_images(input_img):
    input_img = tf.cast(input_img, tf.float32)
    input_img = (input_img - 127.5) / 127.5
    return input_img

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_sketch", methods=["POST"])
def generate_sketch():
    # Get the uploaded sketch file
    sketch = request.files["sketch"]
    image = Image.open(sketch)

    # Process the sketch for the Generator model
    image = image.convert("RGB")
    image = image.resize((256, 256))
    image_array = np.array(image)

    # Normalize the image
    normalized_image = Normalize_images(image_array)
    normalized_image = np.expand_dims(normalized_image, axis=0)

    # Generate the image using the Generator model
    generated_image = generator_model.predict(normalized_image)[0]
    generated_image = ((generated_image * 127.5) + 127.5).astype(np.uint8)
    generator_output_image = Image.fromarray(generated_image)

    # Convert the generator model image to base64 for JSON response
    generator_image_base64 = image_to_base64(generator_output_image)

    return jsonify({
        "generatorImage": f"data:image/png;base64,{generator_image_base64}"
    })

@app.route("/generate_prompt", methods=["POST"])
def generate_prompt():
    # Get the prompt from the form
    prompt = request.form.get("prompt")
    
    # Send the prompt to the Hugging Face API
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

    if response.status_code == 200:
        # The response is an image in the content
        api_image = Image.open(io.BytesIO(response.content))

        # Convert the generated image to base64 for the frontend to display
        prompt_image_base64 = image_to_base64(api_image)

        return jsonify({"promptImage": f"data:image/png;base64,{prompt_image_base64}"})
    else:
        return jsonify({"error": "Failed to generate image from prompt."}), 400

if __name__ == "__main__":
    app.run(debug=True)
