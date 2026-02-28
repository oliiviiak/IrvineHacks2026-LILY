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
        return image_path.base64.b64encode(image_file.read()).decode('utf-8')



        

def handle_tool(call):
    args = json.loads(call.function.arguments)
    if call.function.name == "take_photo":
        return
    elif call.function.name == "record_audio":
        return


def run(user_message, model="anthropic/claude-sonnet-4-5-20250929"):
    messages = [{"role": "user", "content": user_message}]

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