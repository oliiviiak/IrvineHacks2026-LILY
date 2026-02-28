import litellm
import json
import base64
from PIL import Image
import pytesseract

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
            "name": "upload_photo",
            "description": "Uploads a photo to the app",
            "parameters": {
                "type": "object",
                "properties": {
                    "timestamp": {
                        "type": "string",
                        "description": "Time when the photo was taken"
                    }

                },
                "required": ["filename"]
            },
        }
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
                    "filename": {"type": "string"}
                },
                "required": ["filename"]
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
                "required": ["document_type", "summary", "urgency"]
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
    return pytesseract.image_to_string(image)


def handle_tool(call):
    args = json.loads(call.function.arguments)
    if call.function.name == "take_photo":
        return
    elif call.function.name == "record_audio":
        return
    elif call.function.name == "analyze_document":
        return
    elif call.function.name == "notify_caretaker":
        return

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
        

def document_summary(image_path: str):
    extracted_text = extract_text_from_image(image_path)
    image_b64 = encode_image(image_path)
    
    prompt = f"""You are a document scanner. Your only job is to report what is physically present in this document.

                <extracted_text>
                {extracted_text}
                </extracted_text>

                Using ONLY the extracted text above, provide:
                1. A summary of each section and what it contains
                2. Any fields that require action (e.g. signature required, date needed, checkbox unchecked)

                Rules:
                - Do NOT analyze, interpret, or give opinions
                - Do NOT add any information not explicitly present in the document
                - Do NOT make inferences
                - Only report what is literally there"""
    
    return run(prompt, image=image_b64)


image_b64 = encode_image("testimg.jpeg")
res = run("What do you see in this image?", image=image_b64)
res1 = run("what do you hear?", audio_transcript="hello hello can you hear me")
res2 = document_summary("testdocument.jpeg")
print(res)
print(res1)
print(res2)
