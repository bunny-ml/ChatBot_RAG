from flask import Flask, request, Response, jsonify, render_template
from app_backend.services.groq_LLM import llm_response
from app_backend.services.file_upload import upload_service
import os
from supabase import create_client, Client
import uuid
       

class Flask_app:
    def __init__(self):
        self.app = Flask(
            __name__,
            static_folder=os.path.abspath('static'),
            template_folder=os.path.abspath("templates")
        )
        self.uploader = upload_service()
        self.configure_routes()

    

    def configure_routes(self):
        # route for the home page or index page
        @self.app.route('/', methods=['GET'])
        def home():
            """ print('[INFO] / route hit')"""

            return render_template('index.html')
    
        # route for the login page
        @self.app.route('/login', methods=['GET'])
        def login():
            """ print('[INFO] /index route hit')"""
            return render_template('login.html')
        
        @self.app.route('/register', methods=['GET'])
        def register():
            """ print('[INFO] /register route hit')"""
            return render_template('register.html')
        

        
        # route for the LLM chat
        @self.app.route('/chat', methods=['POST'])
        def chat_llm():
            data = request.get_json()

            user_query = data.get('user_query')
            context_data = data.get('context_data', None)

            return Response(llm_response(user_query, context_data), mimetype="text/plain")

        # route for the file upload
        @self.app.route('/upload', methods=['POST'])
        def upload():
            return self.uploader.upload()



         # use file storage system to upload files (google drive, s3, etc.)
        # @self.app.route('/upload' , methods=['POST'])
        # def upload():
        #     if 'file' not in request.files:
        #         return jsonify({"error": "No file part"}), 400
            
        #     file = request.files['file']
        #     if file.filename == '':
        #         return jsonify({"error": "No selected file"}), 400
            
        #     uploads = os.path.abspath('uploads')
        #     os.makedirs(uploads, exist_ok=True)
            
        #     file_path = os.path.join(uploads, file.filename)
        #     try:
        #         file.save(file_path)
        #         return jsonify({'message': "File uploaded successfully"}), 200
        #     except Exception as e:
        #         print("error:" f"File upload failed: {str(e)}"), 500
        #     return jsonify({"error:" f"File upload failed: {str(e)}"}), 500

    def get_app(self):
        return self.app
