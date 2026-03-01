import os
import sqlite3

import create_functions

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "db", "app.db")

connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row

def get_convo(convo_id):
    cursor = connection.cursor()
    transcript_data = {}
    alerts_data = {}
    documents_data = []

    # get transcript_items
    transcript_query = "SELECT * FROM transcript_items WHERE id = ?"
    cursor.execute(transcript_query, (convo_id,))

    t_result = cursor.fetchone()
    if t_result:
        transcript_data = dict(t_result)

    # get alerts
    transcript_item_id = transcript_data["transcript_item_id"]
    alert_query = "SELECT * FROM alerts WHERE transcript_item_id = ?"
    cursor.execute(alert_query, (transcript_item_id, ))
    
    a_result = cursor.fetchone()
    if a_result:
        alerts_data = dict(a_result)

    #get documents
    documents_query = "SELECT * FROM documents WHERE id = ?"
    cursor.execute(documents_query, (convo_id,))

    d_result = cursor.fetchall()
    documents_data = [dict(d) for d in d_result] if d_result else []

    return {
        "transcripts": transcript_data,
        "alerts": alerts_data,
        "documents": documents_data
    }


convo_id = create_functions.create_convo("1")
doc_id = create_functions.create_document(convo_id, "doc summary!!", "contentnntnntn")
trans_id = create_functions.create_transcript_item(convo_id, "izzy", "transcirptcnotentntntn")
alert_id = create_functions.create_alert(doc_id, "hi!!", trans_id)

answer = get_convo(convo_id)

print("transcript: " + answer["transcripts"])
print("alerst: " + answer["alerts"])
print("documents: " + answer["documents"])
    