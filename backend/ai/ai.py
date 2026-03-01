import litellm
import json
import base64
from PIL import Image
import pytesseract
import cv2
import os
import datetime
from db.db import db
import features.create_functions as create_functions
import uuid

from dotenv import load_dotenv
load_dotenv()

# take_photo and record_audio removed — the microcontroller is a separate
# physical device that handles camera and audio itself, posting to the backend
# over HTTP. The AI never needs to trigger hardware.
tools = [
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
                "properties": {
                    "caretaker_notified": {"type": "object"},
                    "document_type": {"type": "string"},
                    "summary": {"type": "string"},
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
        x, y, w, h = line["x"], line["y"], line["width"], line["height"]
        text = " ".join(line["words"])
        result += f"[LN:{global_line_num}][{x} {y} {w} {h}] {text}\n"

    return result


def get_latest_doc_id(convo_id: str) -> str | None:
    row = db.execute(
        "SELECT document_id FROM documents WHERE convo_id = ? ORDER BY created_at DESC LIMIT 1",
        (convo_id,)
    ).fetchone()
    return row["document_id"] if row else None


def handle_tool(call, convo_id: str = None):
    args = json.loads(call.function.arguments)

    if call.function.name == "analyze_document":
        return document_summary(args["text"])

    elif call.function.name == "notify_caretaker":
        summary  = args["summary"]
        urgency  = args["urgency"]
        doc_type = args["document_type"]

        doc_id = get_latest_doc_id(convo_id) if convo_id else None

        if doc_id:
            message = f"[{urgency.upper()}] {doc_type}: {summary}"
            create_functions.create_alert(doc_id=doc_id, message=message)
            print(f"[notify_caretaker] alert created for doc {doc_id}: {message}")
        else:
            print(f"[notify_caretaker] no doc found for convo {convo_id}, alert not saved")

        return {"status": "success"}


def run(user_message, model="anthropic/claude-sonnet-4-5-20250929", image: str = None, mime_type: str = "image/jpeg", audio_transcript: str = None, convo_id: str = None):

    system = """You are LILY, an assistant for caregiving. Only call the notify_caretaker tool if the user
            explicitly asks you to send an alert or notify their caretaker. Never call it on your own judgment.
            """

    content = user_message
    if audio_transcript:
        content += f"\n\nAudio transcript: {audio_transcript}"

    if image:
        content = [
            {"type": "image_url", "image_url": {"url": build_data_url(image, mime_type)}},
            {"type": "text", "text": content}
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
                result = handle_tool(call, convo_id=convo_id)
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
                2. A concise summary of the most important sections
                3. Any fields that require action (e.g. signature required, date needed, checkbox unchecked)

                Rules:
                - Do NOT analyze, interpret, or give opinions
                - Do NOT add any information not explicitly present in the document
                - Do NOT make inferences
                - Only report what is literally there"""

    return run(prompt, image=image_b64)


def start_conversation(needer_id: str):
    convo_id = create_functions.create_convo(needer_id)

    print("Say 'hi lily' to start...")

    while True:
        user_input = input("You: ")

        if "bye lily" in user_input.lower():
            print("Lily: Goodbye!")
            break

        if "hi lily" in user_input.lower():
            print("Lily: Hi! How can I help you?")
            continue

        create_functions.create_transcript_item(convo_id, "careneeder", user_input)
        lily_response = run(user_input, convo_id=convo_id)
        create_functions.create_transcript_item(convo_id, "LILY", lily_response)

        print(f"Lily: {lily_response}")

    return convo_id


if __name__ == "__main__":
    test_user_id = str(uuid.uuid4())
    db.execute("INSERT INTO users (id, provider, subject) VALUES (?, ?, ?)", (test_user_id, "email", "test@test.com"))
    db.execute("INSERT INTO careneeders (user_id, first_name, last_name) VALUES (?, ?, ?)", (test_user_id, "Test", "User"))
    db.commit()
    start_conversation(test_user_id)