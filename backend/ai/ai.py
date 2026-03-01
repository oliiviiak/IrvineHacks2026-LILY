import litellm
import json
import base64
import cv2
import subprocess
import os

import datetime

from dotenv import load_dotenv
load_dotenv()

# Works with both providers, same interface
tools = [
    {
        "type": "function",
        "function": {
            "name": "take_photo",
            "description": "Capture a photo from the webcam",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },

    {
        "type": "function",
        "function": {
            "name": "record_audio",
            "description": "Record audio from microphone",
            "parameters": {
                "type": "object",
                "properties": {"duration": {"type": "integer"}},
                "required": ["duration"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "analyze_document",
            "description": "Analyzes and summarizes the document",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "notify_caretaker",
            "description": "Notifies the caretaker for each document uploaded and analyzed",
            "parameters": {
                "type": "object",
                "properties":{
                    "caretaker_notified": {
                        "type": "object"
                    },
                    "document_type": {
                        "type": "string"
                    },
                    "summary": {
                        "type": "string"
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["low", "medium", "high"]
                    }
                },
                "required": ["document_type", "summary", "urgency", "caretaker_notified"]
            }
        }
    }

]


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def build_data_url(base64_string: str, mime_type: str = "image/jpeg") -> str:
    return f"data:{mime_type};base64,{base64_string}"
        

def handle_tool(call):
    args = json.loads(call.function.arguments)
    if call.function.name == "take_photo":
        micro_main = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../microcontroller/main.py"))
        subprocess.run(["python3", micro_main])
        img = cv2.imread("photo.jpg")
        if img is None:
            return "Failed to load image"
        return img
    elif call.function.name == "record_audio":
        micro_main = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../microcontroller/main.py"))
        subprocess.run(["python3", micro_main])
        aud = cv2.imread("recording.wav")
        return aud
    elif call.function.name == "analyze_document":
        return
    elif call.function.name == "notify_caretaker":
        info = {
            "caretake_notified": args.get("caretaker_notified", {}),
            "document_type": args["document_type"],
            "summary": args["summary"],
            "urgency": args["urgency"],
            "timestamp": str(datetime.datetime.now())
        }

        print("Notifying caretaker:", json.dumps(info, indent=2))
        return {"status": "success"}

def run(user_message, model="anthropic/claude-sonnet-4-5-20250929", image: str = None, mime_type: str = "image/jpeg", audio_transcript: str = None):
    
    content = user_message
    if audio_transcript:
        content += f"\n\nAudio transcript: {audio_transcript}"

    if image:
        content = [
            {
                "type": "image_url",
                "image_url": {"url": build_data_url(image, mime_type)}
            },
            {
                "type": "text",
                "text": content
            }
        ]
    
    messages = [{"role": "user", "content": content}]

    while True:
        response = litellm.completion(model=model, messages=messages, tools=tools)
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                result = handle_tool(call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result),
                })
        else:
            return msg.content

#image_b64 = encode_image("testimg.jpeg")
#res = run("What do you see in this image?", image=image_b64)
#res1 = run("what do you hear?", audio_transcript="hello hello can you hear me")

res = run("record audio for 10 secs")
print(res)