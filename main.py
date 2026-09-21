import os
import requests
from google import genai

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
PAGE_ID = os.environ["PAGE_ID"]
PAGE_ACCESS_TOKEN = os.environ["PAGE_ACCESS_TOKEN"]

client = genai.Client(api_key=GEMINI_API_KEY)

prompt = """
Urdu mein ek chhota aur interesting science ya psychology fact likho.
Sirf ek fact likho.
2 chhoti lines hon.
Koi hashtag, emoji ya extra explanation nahi.
"""

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

fact = response.text.strip()

print("FACT:")
print(fact)

url = f"https://graph.facebook.com/v26.0/{PAGE_ID}/feed"

data = {
    "message": fact,
    "access_token": PAGE_ACCESS_TOKEN
}

response = requests.post(
    url,
    data=data,
    timeout=60
)

print("FACEBOOK RESPONSE:")
print(response.text)

if not response.ok:
    raise RuntimeError(
        f"Facebook posting failed: {response.text}"
    )

print("FACEBOOK POST SUCCESSFUL!")
