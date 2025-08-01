from flask import Flask, request, Response, jsonify, render_template
from app_backend.services.groq_LLM import llm_response

class Flask_app:
    def __init__(self):
        self.app = Flask(
            __name__,
            static_folder='/home/bunny/Desktop/Coding/ChatBot_RAG/static',
            template_folder="/home/bunny/Desktop/Coding/ChatBot_RAG/templates"
        )
        self.configure_routes()

    def configure_routes(self):
        @self.app.route('/', methods=['GET'])
        def home():
            # print('[INFO] / route hit')
            return render_template('index.html')

        @self.app.route('/chat', methods=['POST'])
        def chat_llm():
            data = request.get_json()

            user_query = data.get('user_query')
            context_data = data.get('context_data', None)

            return Response(llm_response(user_query, context_data), mimetype="text/plain")

        @self.app.route('/upload' , methods=['POST'])
        def upload():
            pass

    def get_app(self):
        return self.app
