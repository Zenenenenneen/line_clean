from fastapi import FastAPI, Request
import requests
import dateparser
from datetime import datetime
from pythainlp.util import normalize
import re

def convert_thai_time(text: str) -> str:
    # Colloquial words
    time_map = {
        "เช้า": "07:00",
        "สาย": "10:00",
        "เที่ยง": "12:00",
        "บ่าย": "13:00",
        "เย็น": "18:00",
        "ค่ำ": "19:00",
        "ดึก": "22:00",
        "กลางคืน": "21:00",
        "คืน": "21:00"
    }
    for word, time in time_map.items():
        if word in text:
            text = text.replace(word, time)

    # Handle "X โมงเช้า/บ่าย/เย็น/คืน"
    match = re.search(r"(\d+)\s*โมง(เช้า|บ่าย|เย็น|ค่ำ|คืน)", text)
    if match:
        hour = int(match.group(1))
        period = match.group(2)

        if period == "เช้า":
            pass  # morning hours (7 โมงเช้า = 07:00)
        elif period == "บ่าย":
            hour += 12 if hour != 12 else 12
        elif period in ["เย็น", "ค่ำ", "คืน"]:
            hour += 12

        text = re.sub(r"\d+\s*โมง(เช้า|บ่าย|เย็น|ค่ำ|คืน)", f"{hour:02d}:00", text)

    # Handle "ครึ่ง"
    match_half = re.search(r"(\d+)\s*โมงครึ่ง", text)
    if match_half:
        hour = int(match_half.group(1))
        text = re.sub(r"\d+\s*โมงครึ่ง", f"{hour:02d}:30", text)

    # Handle "ตรง"
    text = text.replace("ตรง", ":00")

    # Handle "ตี X" (early morning)
    match_ti = re.search(r"ตี\s*(\d+)", text)
    if match_ti:
        hour = int(match_ti.group(1))
        text = re.sub(r"ตี\s*\d+", f"{hour:02d}:00", text)

    return text


app = FastAPI()

LINE_ACCESS_TOKEN = "c3PJNA5FEDEdTYioXHXQU85hM7YLrDZSpm13BdFQB8NkgssQAAJD9H01z1+HwdYy1kf2xVeKqxjfW/v7crQm7aN6XRjN4foYjysJRiBZvVfQISvy8UUgga+K/JomzyA/Xh/17YNLYT//opvnkYrebAdB04t89/1O/w1cDnyilFU="

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Server is live!"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("Incoming LINE event:", data)

    for event in data["events"]:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_message = event["message"]["text"]
            normalized = normalize(user_message)
            normalized = convert_thai_time(normalized)
            parsed = dateparser.parse(
                normalized,
                languages=['th','en'],
                settings={
                    'RELATIVE_BASE': datetime.now(),
                    'PREFER_DATES_FROM': 'future'
                }
            )

            if parsed:
                reply_text = f"ได้เลยค่า แอดมินจะจดไว้นะคะ เจอกันค่าา ({parsed.strftime('%Y-%m-%d %H:%M')})"
            elif user_message.lower() in ["hi", "hello"]:
                reply_text = "Hey there! 👋"
            elif "bye" in user_message.lower():
                reply_text = "Goodbye, take care!"
            elif "help" in user_message.lower():
                reply_text = "Sure, what do you need help with?"
            elif "จอง Private class ka" in user_message:
                reply_text = "ได้เลยค่า กรุณาแจ้งวันและเวลาที่สนใจไว้เลยนะคะ"

            # --- Reply to LINE ---
            requests.post(
                "https://api.line.me/v2/bot/message/reply",
                headers={
                    "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "replyToken": event["replyToken"],
                    "messages": [{"type": "text", "text": reply_text}]
                }
            )

    return {"status": "ok"}
