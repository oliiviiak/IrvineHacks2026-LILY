import litellm
import json

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

                }
            },
            "required": ["filename"]
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