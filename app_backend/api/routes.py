from flask import Flask , request , Response , jsonify
from app.services.groq_LLM import llm_response

class Flask_app:
    def __init__(self):
        self.app = Flask(__name__) 
        self.configure_routes()

    def configure_routes(self):
        @self.app.route('/test', methods = ['GET'])
        def method_name():
            return "app is runnig"


        @self.app.route('/chat', methods = ['POST'])
        def chat_llm():
            data = request.get_json()
            user_query = data.get('user_query')
            context_data = data.get('context_data', None)

            if not user_query :
                return jsonify({"error":"Missing 'user_query'"}), 400 
            return Response(llm_response(user_query , context_data), mimetype="text/plain")           

    def run(self, debug=True):
        self.app.run(debug=debug)
