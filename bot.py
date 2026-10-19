import os
import json
import time
import random
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIG ─────────────────────────────────────────────────────────────────────
CHARACTER = os.getenv("CHARACTER_PROMPT", "neon-haired cyberpunk girl")
NICHE = os.getenv("NICHE", "1980s retro futuristic streetwear")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./generated")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── SCENARIOS ──────────────────────────────────────────────────────────────────
SCENARIOS = [
    "driving a retro hovercar through neon rain",
    "playing arcade games in a dimly lit arcade",
    "sipping synthetic coffee at a rooftop bar",
    "walking past holographic advertisements",
    "tuning a vintage synth in a garage",
    "hacking a mainframe with glowing cables"
]

def get_random_scenario():
    return random.choice(SCENARIOS)

# ─── IMAGE GENERATION (Replicate) ───────────────────────────────────────────────
def generate_image(prompt: str) -> str:
    url = "url = "https://api.replicate.com/v1/models/black-forest-labs/flux-1.1/predictions"
"
    headers = {
        "Authorization": f"Token {os.getenv('REPLICATE_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": {
            "prompt": f"{CHARACTER}, {prompt}, highly detailed, cinematic lighting, 16:9 aspect ratio",
            "num_outputs": 1,
            "aspect_ratio": "16:9"
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    prediction_url = response.json()["urls"]["get"]

    while True:
        status_resp = requests.get(prediction_url, headers=headers)
        data = status_resp.json()
        status = data.get("status")

        if status == "succeeded":
            image_url = data["output"][0]
            img_path = os.path.join(OUTPUT_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            img_data = requests.get(image_url).content
            with open(img_path, "wb") as f:
                f.write(img_data)
            return img_path

        if status == "failed":
            raise Exception("Image generation failed")

        time.sleep(5)

# ─── CAPTION GENERATION (OpenAI) ────────────────────────────────────────────────
def generate_caption() -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": (
                "Write a short, engaging Instagram caption for a retro-futuristic AI art post. "
                "Tone: mysterious, cool, slightly nostalgic. Max 2 sentences. No hashtags."
            )
        }],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

# ─── MERCH TEXT OVERLAY ─────────────────────────────────────────────────────────
def add_merch_text(img_path: str) -> str:
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    text = f"DAY {datetime.now().day} | {CHARACTER.split()[0].upper()}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    x = (img.width - text_w) // 2
    y = img.height - text_h - 20

    draw.rectangle((x-10, y-10, x+text_w+10, y+text_h+10), fill="#000000")
    draw.text((x, y), text, fill="#ffffff", font=font)

    merch_path = img_path.replace(".jpg", "_merch.jpg")
    img.save(merch_path)
    return merch_path

# ─── REDBUBBLE PRIVATE API UPLOADER ────────────────────────────────────────────
RB_SESSION = os.getenv("RB_SESSION")
RB_OPENID = os.getenv("RB_OPENID")
RB_REFRESH = os.getenv("RB_REFRESH")

RB_HEADERS = {
    "Cookie": f"_rb_session4={RB_SESSION}; open_id_token={RB_OPENID}; refresh_token={RB_REFRESH}",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

def rb_upload_image(img_path: str):
    url = "https://www.redbubble.com/studio/items/upload"
    files = {"file": open(img_path, "rb")}

    response = requests.post(url, headers=RB_HEADERS, files=files)
    if response.status_code != 200:
        raise Exception(f"Redbubble upload failed: {response.text}")

    data = response.json()
    item_id = data["id"]
    print("Uploaded image. Item ID:", item_id)
    return item_id

def rb_update_metadata(item_id: str, title: str, tags: list):
    url = f"https://www.redbubble.com/studio/items/{item_id}/update"
    payload = {
        "title": title,
        "tags": tags,
        "mediaType": "design",
        "isMatureContent": False,
    }

    response = requests.post(url, headers=RB_HEADERS, json=payload)
    if response.status_code != 200:
        raise Exception(f"Metadata update failed: {response.text}")

    print("Updated metadata.")
    return True

def rb_publish(item_id: str):
    url = f"https://www.redbubble.com/studio/items/{item_id}/publish"
    response = requests.post(url, headers=RB_HEADERS)
    if response.status_code != 200:
        raise Exception(f"Publish failed: {response.text}")

    print("Published design.")
    return True

def upload_to_redbubble(img_path: str, title: str, tags: list):
    print("Uploading to Redbubble...")
    item_id = rb_upload_image(img_path)
    rb_update_metadata(item_id, title, tags)
    rb_publish(item_id)
    print("Redbubble upload complete.")

# ─── INSTAGRAM POST ────────────────────────────────────────────────────────────
def post_to_instagram(img_path: str, caption: str):
    url = "https://graph.instagram.com/me/media"
    headers = {"Authorization": f"Bearer {os.getenv('INSTAGRAM_ACCESS_TOKEN')}"}

    with open(img_path, "rb") as f:
        files = {"image": f}
        data = {"caption": caption, "is_carousel_media_item": "true"}
        res1 = requests.post(url, headers=headers, files=files, data=data)
        res1.raise_for_status()
        container_id = res1.json()["id"]

    publish_url = "https://graph.instagram.com/me/media_publish"
    res2 = requests.post(publish_url, headers=headers, data={"creation_id": container_id})
    res2.raise_for_status()

    print(f"Posted to Instagram: {res2.json().get('id')}")

# ─── MAIN DAILY TASK ───────────────────────────────────────────────────────────
def daily_task():
    print("Running Infinite Persona Engine...")

    try:
        scenario = get_random_scenario()
        print(f"Generating image: {scenario}")
        raw_img = generate_image(scenario)

        caption = generate_caption()
        print(f"Caption: {caption}")

        merch_img = add_merch_text(raw_img)

        upload_to_redbubble(
            merch_img,
            f"AI Cyberpunk Art - Day {datetime.now().day}",
            ["cyberpunk", "retro", "ai art", "digital design", "streetwear"]
        )

        post_to_instagram(merch_img, caption)

        print("Daily cycle complete.")

    except Exception as e:
        print(f"Error: {e}")

# ─── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    daily_task()
