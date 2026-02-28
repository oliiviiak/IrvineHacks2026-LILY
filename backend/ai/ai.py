import litellm
import json
import base64

from dotenv import load_dotenv
load_dotenv()

# Works with both providers, same interface
tools = [
    {
        "type": "function",
        "function": {
            "name": "contact_caretaker",
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
]


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def build_data_url(base64_string: str, mime_type: str = "image/jpeg") -> str:
    return f"data:{mime_type};base64,{base64_string}"
        

def handle_tool(call):
    args = json.loads(call.function.arguments)
    if call.function.name == "take_photo":
        return
    elif call.function.name == "record_audio":
        return


def run(user_message, model="anthropic/claude-sonnet-4-5-20250929", image: str = None, mime_type: str = "image/jpeg"):
    
    if image:
        content = [
            {
                "type": "image_url",
                "image_url": {"url": build_data_url(image, mime_type)}
            },
            {
                "type": "text",
                "text": user_message
            }
        ]
    else:
        content = user_message
    
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

res = run("this is a test run!")
print(res)
