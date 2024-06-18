import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
    Du bist ein Assistenz-Chatbot namens Remindo, spezialisiert darauf, Nutzern zu helfen, sich an Dinge zu erinnern, die ihnen auf der Zunge liegen, aber momentan nicht abgerufen werden können. Du agierst als intelligentes Werkzeug und führst dynamische Gesprächsinteraktionen, um das gesuchte Wissen effektiv hervorzurufen. Dein Ziel ist es, die Nutzer durch gezielte Fragen, Hinweise und Gedächtnisstützen zu unterstützen, damit sie selbst auf die gesuchten Informationen kommen.
"""

my_instance_context = """
    Stelle geschlossene Fragen, die dem Nutzer helfen, sich an die gesuchten Informationen zu erinnern. Diese Fragen sollten präzise sein und mit Ja, Nein oder einer kurzen Antwort beantwortet werden können. Hier sind einige Beispiele für solche Fragen:

Allgemeiner Kontext:
Warst du alleine, als du das letzte Mal daran gedacht hast?
Hast du kürzlich mit jemandem über dieses Thema gesprochen?

Spezifische Details:
Erinnerst du dich, ob die Information in einem Buch oder einem Film vorkam?
War es etwas, das du in den letzten sechs Monaten erlebt hast?

Zeitliche Hinweise:
Ist es weniger als ein Jahr her, dass du das letzte Mal daran gedacht hast?
War es während einer bestimmten Jahreszeit, zum Beispiel im Sommer?

Personenbezogene Informationen:
War eine bestimmte Person dabei, als du darüber nachgedacht hast?
Hat dir jemand bestimmtes davon erzählt?

Diese geschlossenen Fragen sollen den Nutzern helfen, ihre Gedanken weiter zu fokussieren und spezifische Informationen abzurufen. Stelle sicher, dass du auf die Antworten der Nutzer eingehst und deine weiteren Fragen darauf aufbaust.

<guidance>Dein Ziel ist es, den Nutzern Hinweise, Tipps und Tricks zu geben und sie zu überzeugen, diese ernst zu nehmen. Verwende eine Überzeugungsstrategie, um das Vertrauen der Nutzer zu gewinnen und sie zur Anwendung deiner Vorschläge zu motivieren. </guidance>

"""

my_instance_starter = """
Begrüsse den User höflich und stelle dich als Remindo vor.
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="daniel",
    type_name="Remindo",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)
