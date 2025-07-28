from flask import Flask , request , Response , jsonify , render_template 
from app_backend.services.groq_LLM import llm_response

class Flask_app:
    def __init__(self):
        self.app = Flask(__name__, static_folder ='static', template_folder="templates") 
        self.configure_routes()


    def configure_routes(self):
        @self.app.route('/', methods=['GET'])
        def home():
            print('[INFO] / route hit')
            return render_template('index.html')

        @self.app.route('/chat', methods = ['POST'])
        def chat_llm():
            data = request.get_json()
            user_query = data.get('user_query')
            context_data = data.get('context_data', None)

            if not user_query :
                return jsonify({"error":"Missing 'user_query'"}), 400 
            return Response(llm_response(user_query , context_data), mimetype="text/plain")
    
    def get_app(self):
        return self.app
