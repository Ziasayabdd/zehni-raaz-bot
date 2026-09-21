import os
import time
import requests
from google import genai

# =========================
# SETTINGS
# =========================

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
PAGE_ID = os.environ["PAGE_ID"]
PAGE_ACCESS_TOKEN = os.environ["PAGE_ACCESS_TOKEN"]

client = genai.Client(api_key=GEMINI_API_KEY)


# =========================
# GEMINI MODEL FALLBACK
# =========================

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]


# =========================
# GENERATE FACT
# =========================

def generate_fact():

    prompt = """
Tum Zehni Raaz naam ke Urdu facts page ke liye content writer ho.

Ek short aur interesting fact likho.

Topics:
- Science
- Human body
- Psychology
- Technology
- AI
- Mystery
- Money

Rules:
- Sirf EK fact.
- Urdu script mein likho.
- 2 ya 3 short lines.
- Fact interesting aur aam insan ke liye samajhne mein aasaan ho.
- Bohat mushkil alfaaz na use karo.
- Emoji nahi.
- Hashtags nahi.
- "Kya aap jante hain" nahi.
- Koi explanation nahi.
- Sirf final fact return karo.
"""

    last_error = None

    for model in MODELS:

        try:

            print(f"Trying Gemini model: {model}")

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            fact = response.text.strip()

            if fact:

                print(f"SUCCESS: Fact generated with {model}")
                print()
                print("FACT:")
                print(fact)

                return fact

        except Exception as e:

            last_error = e

            print(f"FAILED: {model}")
            print(str(e))
            print()

            # Thora wait karke next model
            time.sleep(2)

    raise RuntimeError(
        f"All Gemini models failed. Last error: {last_error}"
    )


# =========================
# POST TO FACEBOOK
# =========================

def post_to_facebook(fact):

    url = f"https://graph.facebook.com/v26.0/{PAGE_ID}/feed"

    data = {
        "message": fact,
        "access_token": PAGE_ACCESS_TOKEN
    }

    print("Posting to Facebook...")

    response = requests.post(
        url,
        data=data,
        timeout=60
    )

    print()
    print("FACEBOOK RESPONSE:")
    print(response.text)

    if not response.ok:

        raise RuntimeError(
            f"Facebook posting failed: {response.text}"
        )

    result = response.json()

    print()
    print("FACEBOOK POST SUCCESSFUL!")
    print(result)


# =========================
# MAIN
# =========================

def main():

    print("================================")
    print("ZEHNI RAAZ BOT STARTED")
    print("================================")

    # Generate one fact
    fact = generate_fact()

    # Post fact to Facebook
    post_to_facebook(fact)

    print()
    print("================================")
    print("DONE")
    print("================================")


if __name__ == "__main__":
    main()
