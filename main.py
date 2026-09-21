
import os
import base64
import textwrap
import requests

from google import genai
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display


# =========================
# SETTINGS
# =========================

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
PAGE_ID = os.environ["PAGE_ID"]
PAGE_ACCESS_TOKEN = os.environ["PAGE_ACCESS_TOKEN"]

OUTPUT_DIR = "output"
FONT_PATH = "assets/jameel.ttf"

os.makedirs(OUTPUT_DIR, exist_ok=True)

client = genai.Client(api_key=GEMINI_API_KEY)


# =========================
# GEMINI TEXT MODELS
# =========================

FACT_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]


# =========================
# GEMINI IMAGE MODELS
# =========================

IMAGE_MODELS = [
    "gemini-3.1-flash-image",
    "gemini-3-pro-image",
]


# =========================
# GENERATE FACT
# =========================

def generate_fact():

    prompt = """
Tum Urdu facts content writer ho.

Ek hi short aur interesting fact likho.

Topic:
- psychology
- human body
- science
- technology
- AI
- mystery
- money

Rules:
- Sirf EK fact.
- Urdu mein likho.
- 2 ya 3 chhoti lines.
- Aisa fact ho jo aam aadmi ko interesting lage.
- Bohat mushkil alfaaz na use karo.
- Hashtags mat do.
- Emoji mat do.
- "Kya aap jante hain" mat likho.
- Koi explanation ya extra text mat do.
- Sirf final fact do.
"""

    last_error = None

    for model in FACT_MODELS:
        try:
            print(f"Trying text model: {model}")

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            fact = response.text.strip()

            if fact:
                print(f"Fact generated with: {model}")
                return fact

        except Exception as e:
            last_error = e
            print(f"Text model failed: {model}")
            print(str(e))

    raise RuntimeError(
        f"All Gemini text models failed. Last error: {last_error}"
    )


# =========================
# GENERATE IMAGE
# =========================

def generate_image(fact):

    prompt = f"""
Create a high-quality realistic vertical social-media background image
for this Urdu fact:

"{fact}"

Requirements:
- Vertical 9:16 composition
- No text inside the image
- No letters
- No captions
- No watermark
- No logo
- One clear visual concept
- The image must visually represent the fact
- Professional social media style
- Strong lighting
- Detailed and realistic
- Keep the center/lower area visually clean enough for Urdu text overlay
"""

    last_error = None

    for model in IMAGE_MODELS:

        try:
            print(f"Trying image model: {model}")

            interaction = client.interactions.create(
                model=model,
                input=prompt,
                response_format={
                    "type": "image",
                    "mime_type": "image/jpeg",
                    "aspect_ratio": "9:16",
                    "image_size": "2K"
                }
            )

            if interaction.output_image:
                image_data = interaction.output_image.data

                image_path = os.path.join(
                    OUTPUT_DIR,
                    "background.jpg"
                )

                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(image_data))

                print(f"Image generated with: {model}")

                return image_path

        except Exception as e:
            last_error = e
            print(f"Image model failed: {model}")
            print(str(e))

    raise RuntimeError(
        f"All Gemini image models failed. Last error: {last_error}"
    )


# =========================
# URDU TEXT
# =========================

def prepare_urdu_text(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


# =========================
# CREATE FINAL 1080x1920
# =========================

def create_final_image(background_path, fact):

    image = Image.open(background_path).convert("RGB")

    # Exact Full HD vertical size
    image = image.resize(
        (1080, 1920),
        Image.Resampling.LANCZOS
    )

    draw = ImageDraw.Draw(image, "RGBA")

    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(
            f"Font not found: {FONT_PATH}"
        )

    font = ImageFont.truetype(
        FONT_PATH,
        62
    )

    small_font = ImageFont.truetype(
        FONT_PATH,
        38
    )

    # Wrap Urdu fact
    lines = textwrap.wrap(
        fact,
        width=25
    )

    prepared_lines = [
        prepare_urdu_text(line)
        for line in lines
    ]

    # Calculate text box
    line_heights = []

    for line in prepared_lines:
        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font
        )
        line_heights.append(
            bbox[3] - bbox[1]
        )

    spacing = 20

    total_height = (
        sum(line_heights)
        + spacing * (len(prepared_lines) - 1)
    )

    # Text area position
    box_width = 930
    box_height = total_height + 120

    box_x = (1080 - box_width) // 2
    box_y = 1920 - box_height - 180

    # Dark transparent background
    draw.rounded_rectangle(
        (
            box_x,
            box_y,
            box_x + box_width,
            box_y + box_height
        ),
        radius=40,
        fill=(0, 0, 0, 165)
    )

    # Draw Urdu lines
    current_y = box_y + 60

    for line, line_height in zip(
        prepared_lines,
        line_heights
    ):

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font
        )

        text_width = bbox[2] - bbox[0]

        x = (1080 - text_width) // 2

        # Shadow
        draw.text(
            (x + 3, current_y + 3),
            line,
            font=font,
            fill=(0, 0, 0, 220)
        )

        # Main text
        draw.text(
            (x, current_y),
            line,
            font=font,
            fill=(255, 255, 255, 255)
        )

        current_y += line_height + spacing

    # Brand
    brand = prepare_urdu_text("ذہنی راز")

    bbox = draw.textbbox(
        (0, 0),
        brand,
        font=small_font
    )

    brand_width = bbox[2] - bbox[0]

    draw.text(
        (
            (1080 - brand_width) // 2,
            70
        ),
        brand,
        font=small_font,
        fill=(255, 255, 255, 230)
    )

    final_path = os.path.join(
        OUTPUT_DIR,
        "zehni_raaz.jpg"
    )

    image.save(
        final_path,
        "JPEG",
        quality=95,
        optimize=True
    )

    print("Final image created:")
    print(final_path)

    return final_path


# =========================
# POST TO FACEBOOK
# =========================

def post_to_facebook(image_path):

    url = f"https://graph.facebook.com/v26.0/{PAGE_ID}/photos"

    with open(image_path, "rb") as image_file:

        response = requests.post(
            url,
            data={
                "access_token": PAGE_ACCESS_TOKEN,
                "published": "true"
            },
            files={
                "source": image_file
            },
            timeout=120
        )

    print("Facebook response:")
    print(response.text)

    if not response.ok:
        raise RuntimeError(
            f"Facebook upload failed: {response.text}"
        )

    print("Facebook post successful!")


# =========================
# MAIN
# =========================

def main():

    print("================================")
    print("ZEHNI RAAZ BOT STARTED")
    print("================================")

    # 1. Fact
    fact = generate_fact()

    print("\nFACT:")
    print(fact)

    # 2. AI image
    background = generate_image(fact)

    # 3. Urdu text overlay
    final_image = create_final_image(
        background,
        fact
    )

    # 4. Facebook
    post_to_facebook(final_image)

    print("\n================================")
    print("DONE")
    print("================================")


if __name__ == "__main__":
    main()
