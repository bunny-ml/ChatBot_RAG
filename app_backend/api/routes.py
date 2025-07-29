from flask_cors import CORS
from flask import Flask, request, Response, jsonify, render_template
from app_backend.services.groq_LLM import llm_response

class Flask_app:
    def __init__(self):
        self.app = Flask(__name__,
                         static_folder='/home/bunny/Desktop/Coding/ChatBot_RAG/static',
                         template_folder="/home/bunny/Desktop/Coding/ChatBot_RAG/templates")
        CORS(self.app)
        self.configure_routes()

    def configure_routes(self):
        @self.app.route('/', methods=['GET'])
        def home():
            print('[INFO] / route hit')
            return render_template('index.html')

        @self.app.route('/chat', methods=['POST'])
        def chat_llm():
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing JSON body"}), 400

            user_query = data.get('user_query')
            context_data = data.get('context_data', None)

            if not user_query:
                return jsonify({"error": "Missing 'user_query'"}), 400

            response_generator = llm_response(user_query, context_data)

            def chat_generator():
                full_response = ""
                for chunk in response_generator:
                    # print(f"[LLM chunk] {chunk}")  # Log each chunk in Flask logs
                    full_response += chunk
                    yield chunk
                # print(f"[LLM full response] {full_response}")

            return Response(chat_generator(), mimetype="text/plain")

    def get_app(self):
        return self.app
