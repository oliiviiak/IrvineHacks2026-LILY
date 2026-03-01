import litellm
import json
import base64
from PIL import Image
import pytesseract
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


# encoding entire image for llm model
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def build_data_url(base64_string: str, mime_type: str = "image/jpeg") -> str:
    return f"data:{mime_type};base64,{base64_string}"


# extractign text from document image
def extract_text_from_image(image_path: str) -> str:
    image = Image.open(image_path)
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    lines = {}
    for i, word in enumerate(data["text"]):
        if word.strip() and int(data["conf"][i]) > 0:
            block_line_key = (data["block_num"][i], data["line_num"][i])
            if block_line_key not in lines:
                lines[block_line_key] = {
                    "words": [],
                    "x": data["left"][i],
                    "y": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i]
                }
            else:
                lines[block_line_key]["width"] = (data["left"][i] + data["width"][i]) - lines[block_line_key]["x"]
            lines[block_line_key]["words"].append(word)
    
    result = ""
    for global_line_num, (key, line) in enumerate(sorted(lines.items()), start=1):
        x = line["x"]
        y = line["y"]
        w = line["width"]
        h = line["height"]
        text = " ".join(line["words"])
        result += f"[LN:{global_line_num}][{x} {y} {w} {h}] {text}\n"
    
    return result


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
        return document_summary(img)
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
    
    system = """You are LILY, an assistant for caregiving. Only call the notify_caretaker tool if the user
            explicitly asks you to send an alert or notify their caretaker. Never call it on your own judgment.
            """
    
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
    
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": content}
    ]

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
        

def document_summary(image_path: str):
    extracted_text = extract_text_from_image(image_path)
    image_b64 = encode_image(image_path)
    
    prompt = f"""You are a document scanner. Your only job is to report what is physically present in this document.

                <extracted_text>
                {extracted_text}
                </extracted_text>

                Using ONLY the extracted text above, provide:
                1. The heading for section and what it contains
                2. A concise summary of the most import sections
                2. Any fields that require action (e.g. signature required, date needed, checkbox unchecked)

                Rules:
                - Do NOT analyze, interpret, or give opinions
                - Do NOT add any information not explicitly present in the document
                - Do NOT make inferences
                - Only report what is literally there"""
    
    return run(prompt, image=image_b64)


# image_b64 = encode_image("testimg.jpeg")
# res = run("What do you see in this image?", image=image_b64)
# res1 = run("what do you hear?", audio_transcript="hello hello can you hear me")
# res2 = document_summary("testdocument.jpeg")
res3 = extract_text_from_image("testdocument.jpeg")
# print(res)
# print(res1)
# print(res2)
print(res3)
