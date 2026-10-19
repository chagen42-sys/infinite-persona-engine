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

    # TURBO / STREET BUILDS
    "a giant turbocharged Nissan GT-R launching flames at night",
    "a twin-turbo Toyota Supra parked under neon city lights",
    "a highly modified street racer making a full boost pull",
    "an anti-lag equipped drift car shooting flames",
    "a turbocharged import car at a late night street meet",

    # DRIFTING
    "a professional drift car sliding through thick tire smoke",
    "a Nissan Silvia drifting through an industrial district",
    "multiple drift cars tandem drifting around a racetrack",
    "a widebody drift car entering a corner at high speed",
    "a drift car lighting up the rear tires during sunset",

    # DRAG RACING
    "a twin-turbo drag car launching off the starting line",
    "a Pro Mod drag car lifting the front wheels",
    "a drag race under bright track lights at night",
    "a nitrous-powered muscle car at the drag strip",
    "a drag racing showdown between two heavily modified cars",

    # MUSCLE CARS
    "a supercharged Dodge Challenger doing a burnout",
    "a classic Chevrolet Camaro cruising through downtown",
    "a modern Ford Mustang with a massive blower",
    "a heavily modified muscle car making a quarter mile run",
    "a blacked-out Dodge Charger beneath storm clouds",

    # SUPERCARS
    "a Lamborghini Aventador driving through mountain roads",
    "a Ferrari hypercar parked in front of a luxury hotel",
    "a McLaren speeding through a futuristic cityscape",
    "a line of exotic supercars at a private car show",
    "a supercar illuminated by neon reflections",

    # HYPERCARS
    "a Bugatti hypercar reaching incredible speeds",
    "a Koenigsegg hypercar parked beside a glass skyscraper",
    "a futuristic hypercar racing through a desert highway",
    "a carbon fiber hypercar under dramatic lighting",
    "a hypercar accelerating through a tunnel at night",

    # JDM CULTURE
    "a lineup of modified JDM legends under neon lights",
    "a heavily customized Mitsubishi Evo on a mountain pass",
    "a Mazda RX-7 parked beside glowing city streets",
    "a classic Skyline cruising through Tokyo-inspired scenery",
    "a Japanese street racing scene after rain",

    # OFF-ROADING
    "a lifted truck climbing a rocky mountain trail",
    "a 4x4 vehicle crossing a river deep in the wilderness",
    "an off-road truck covered in mud after a trail ride",
    "a Jeep crawling over massive boulders",
    "a rugged overland vehicle exploring remote terrain",

    # MUDDING
    "a lifted diesel truck blasting through a mud pit",
    "an off-road competition truck covered in mud",
    "a 4x4 throwing mud high into the air",
    "a muddy trail ride through dense forest terrain",
    "a monster truck conquering an extreme mud bog",

    # DIRT BIKES
    "a dirt bike rider flying over a motocross jump",
    "a motocross race happening during sunset",
    "a dirt bike tearing through a muddy track",
    "a freestyle motocross rider performing an aerial trick",
    "a motocross bike kicking up dirt around a berm",

    # SPORT BIKES
    "a sport bike rider leaning through a mountain corner",
    "a superbike parked under city lights at night",
    "a high-speed motorcycle race on a professional circuit",
    "a custom sport bike with aggressive styling",
    "a superbike rider accelerating out of a corner",

    # COMBINED CAR CULTURE
    "an epic automotive festival featuring supercars and drift cars",
    "a sunset car meet packed with modified performance vehicles",
    "a line of boosted imports and muscle cars",
    "a cinematic scene showing the evolution of performance cars",
    "a gathering of racers, tuners, and gearheads celebrating car culture"

]
]


def default_tags():
    return [
        "turbo",
        "turbocharged",
        "supercharger",
        "boosted",
        "performance",
        "horsepower",
        "streetracing",
        "dragracing",
        "drift",
        "drifting",
        "burnout",
        "jdm",
        "importtuner",
        "musclecar",
        "supercar",
        "hypercar",
        "exoticcars",
        "sportscar",
        "racecar",
        "trackday",
        "motorsports",
        "carculture",
        "carenthusiast",
        "automotive",
        "fastcars",
        "gearhead",
        "offroad",
        "offroading",
        "4x4",
        "mudding",
        "liftedtrucks",
        "rockcrawling",
        "utv",
        "atv",
        "dirtbike",
        "sportbike",
        "motorcycle",
        "superbike",
        "bikelife",
        "racinglife"
    ]

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
