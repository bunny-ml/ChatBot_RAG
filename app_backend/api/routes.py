from flask import Flask, request, Response, jsonify, render_template, make_response, redirect, url_for
from flask_cors import CORS, cross_origin
from app_backend.services.groq_LLM import llm_response
from app_backend.services.file_handler import file_handler_service
import os
import jwt
       

class Flask_app:
    def __init__(self):
        self.app = Flask(
            __name__,
            static_folder=os.path.abspath('static'),
            template_folder=os.path.abspath("templates")
        )
        self.file_handle = file_handler_service()
        CORS(self.app, support_credentials=True)
        self.SUPABASE_JWT_SECRET = os.getenv('JWT_SECRET')
        self.configure_routes()

    def configure_routes(self):
        # route for the home page or index page
        @self.app.route('/', methods=['GET'])
        def home():
            """ print('[INFO] / route hit')"""
            try:
               
                return render_template('login.html',  
                                       SUPABASE_URL = os.getenv('SUPABASE_URL'),
                                       ANON_KEY = os.getenv('ANON_KEY'))
            except:
                return jsonify({f"error":"there is an internal server error 500"}), 500
            
        @self.app.route('/chat_ai', methods=['GET'])
        def chat():
            token = request.cookies.get("access_token")
            # print(f"Received token: {token}")
            if not token:
                return jsonify({"error": "Not logged in"}), 401
            try:
                return render_template('index.html',
                                                    SUPABASE_URL = os.getenv('SUPABASE_URL'),
                                                    ANON_KEY = os.getenv('ANON_KEY'))
            except:
                return jsonify({'error'"something went wrong"}), 500

        # set session
        @self.app.route('/set-session', methods=['POST'])
        @cross_origin(supports_credentials=True)
        def set_session():
            data = request.get_json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")

            if not access_token:
                return jsonify({"error": "Missing token"}), 400

            resp = make_response(redirect(url_for('redirecting')))
            # access token
            resp.set_cookie("access_token", access_token, httponly=True, secure = True , samesite="Lax" , max_age=3600)
            # refresh token 
            resp.set_cookie("refresh_token", refresh_token , httponly=True , secure=True ,samesite="Lax", max_age=604800 )
            return resp
        
        # Add a new route for the temporary redirecting page
        @self.app.route('/redirecting', methods=['GET'])
        def redirecting():
            return render_template('redirecting.html')
        
    

        @self.app.route('/logout', methods=["POST"])
        def logout():
        
            SUPABASE_URL = os.getenv('SUPABASE_URL')
            ANON_KEY = os.getenv('ANON_KEY')
            return SUPABASE_URL, ANON_KEY


        
            


        # route for the login page
        @self.app.route('/login', methods=['GET'])
        def login():
            """ print('[INFO] /index route hit')"""
            try:
                return render_template('login.html',
                                       SUPABASE_URL = os.getenv('SUPABASE_URL'),
                                       ANON_KEY = os.getenv('ANON_KEY'))
            except:
                return jsonify({"error":"there is an internel server error check again later :)"}), 500

        # route for the register or signin
        @self.app.route('/register', methods=['GET'])
        def register():
            """ print('[INFO] /register route hit')"""
            try:
                return render_template('register.html',
                                       SUPABASE_URL = os.getenv('SUPABASE_URL'),
                                       ANON_KEY = os.getenv('ANON_KEY'))
            except:
                return jsonify({"error":"there is an error check again later :)"}), 500

        
        # route for the LLM chat
        @self.app.route('/chat', methods=['POST'])
        def chat_llm():
            token = request.cookies.get("access_token")
            # print(f"Received token: {token}")
            if not token:
                return jsonify({"error": "Not logged in"}), 401
            
            try:
                token_bytes = token.encode('utf-8')
                secret_bytes = self.SUPABASE_JWT_SECRET.encode('utf-8')

                decoded = jwt.decode(token_bytes, secret_bytes, audience="authenticated", algorithms=["HS256"])
                # email = decoded.get("email", "Unknown")
                user_id = decoded.get('sub')
                
                data = request.get_json()


                user_query = data.get('user_query')
                context_chunks = self.file_handle.retrieve_relevant_chunks(user_query,user_id, top_k=5)
                context_data = "\n".join(context_chunks)
                    

                return Response(llm_response(user_id , user_query, context_data), mimetype="text/plain")

                
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 403
            except jwt.InvalidTokenError as e:
                print(f"JWT InvalidTokenError: {e}")
                return jsonify({"error": "Invalid token"}), 403
            

        # route for the file upload
        @self.app.route('/upload', methods=['POST'])
        def upload():
            return self.file_handle.upload_with_auto_delete()


    def get_app(self):
        return self.app
