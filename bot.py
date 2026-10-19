import os
import json
import time
import random
import requests

from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ──────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")

CHARACTER = os.getenv(
    "CHARACTER_PROMPT",
    "neon-haired cyberpunk girl"
)

NICHE = os.getenv(
    "NICHE",
    "1980s retro futuristic streetwear"
)

OUTPUT_DIR = os.getenv(
    "OUTPUT_DIR",
    "./generated"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

client = OpenAI(api_key=OPENAI_API_KEY)

# ──────────────────────────────────────────────────────
# SCENARIOS
# ──────────────────────────────────────────────────────

SCENARIOS = [
    "driving a retro hovercar through neon rain",
    "playing arcade games in a dimly lit arcade",
    "sipping synthetic coffee at a rooftop bar",
    "walking past holographic advertisements",
    "tuning a vintage synth in a garage",
    "hacking a glowing mainframe"
]


def default_tags():
    return [
        "cyberpunk",
        "synthwave",
        "retrofuturism",
        "neon",
        "scifi",
        "digitalart",
        "arcade",
        "future",
        "vaporwave",
        "retrogaming",
        "cyberpunkart",
        "wallart",
        "aesthetic",
        "streetwear",
        "aiart"
    ]


def random_scenario():
    return random.choice(SCENARIOS)

# ──────────────────────────────────────────────────────
# IMAGE GENERATION
# ──────────────────────────────────────────────────────

def generate_image(prompt):

    url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"

    headers = {
        "Authorization": f"Token {REPLICATE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9"
        }
    }

    print("Creating image...")

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    response.raise_for_status()

    prediction_url = response.json()["urls"]["get"]

    while True:

        poll = requests.get(
            prediction_url,
            headers=headers
        )

        poll.raise_for_status()

        data = poll.json()

        status = data["status"]

        print("Image status:", status)

        if status == "succeeded":

            image_url = data["output"][0]

            filename = (
                datetime.now()
                .strftime("%Y%m%d_%H%M%S")
            )

            image_path = os.path.join(
                OUTPUT_DIR,
                f"{filename}.jpg"
            )

            image_data = requests.get(image_url).content

            with open(image_path, "wb") as f:
                f.write(image_data)

            return image_path

        if status == "failed":
            raise Exception("Image generation failed")

        time.sleep(3)


# ──────────────────────────────────────────────────────
# GPT METADATA GENERATION
# ──────────────────────────────────────────────────────

def generate_metadata(scenario):

    prompt = f"""
You are writing metadata for a Printify product.

Scenario:
{scenario}

Return ONLY valid JSON.

Format:

{{
  "title": "",
  "description": ""
}}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.8
    )

    try:
        metadata = json.loads(
            response.choices[0].message.content
        )

        metadata["tags"] = default_tags()

        return metadata

    except Exception:

        return {
            "title": "Cyberpunk Artwork",
            "description": "AI generated cyberpunk artwork.",
            "tags": default_tags()
        }


# ──────────────────────────────────────────────────────
# SAVE METADATA
# ──────────────────────────────────────────────────────

def save_metadata(image_path, metadata):

    metadata_path = image_path.replace(
        ".jpg",
        ".json"
    )

    with open(metadata_path, "w") as f:
        json.dump(
            metadata,
            f,
            indent=2
        )

    return metadata_path


# ──────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────

def main():

    print("\n====================")
    print("INFINITE PERSONA ENGINE")
    print("====================\n")

    scenario = random_scenario()

    print("Scenario:")
    print(scenario)

    image_prompt = (
        f"{CHARACTER}, "
        f"{scenario}, "
        f"{NICHE}, "
        f"cinematic lighting, "
        f"ultra detailed, "
        f"high quality concept art"
    )

    image_path = generate_image(
        image_prompt
    )

    metadata = generate_metadata(
        scenario
    )

    metadata_path = save_metadata(
        image_path,
        metadata
    )

    print("\nSUCCESS\n")

    print("Image:")
    print(image_path)

    print("\nMetadata:")
    print(metadata_path)

    print("\nTitle:")
    print(metadata["title"])

    print("\nDescription:")
    print(metadata["description"])

    print("\nTags:")
    print(", ".join(metadata["tags"]))


if __name__ == "__main__":
    main()
