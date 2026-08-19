from fastapi import FastAPI, Request
import requests
import dateparser
from datetime import datetime

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

            parsed = dateparser.parse(
                user_message,
                languages=['th','en'],
                settings={'RELATIVE_BASE': datetime.now()}
            )

            if parsed:
                reply_text = f"ได้เลยค่า แอดมินจะจดไว้นะคะ เจอกันค่าา ({parsed.strftime('%Y-%m-%d %H:%M')})"

            # --- Hardcoded replies ---
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
