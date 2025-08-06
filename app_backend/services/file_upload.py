from supabase import create_client, Client
from flask import request , jsonify
import os
import uuid

class upload_service:
    def __init__(self):
            self.SUPABASE_URL = "https://imbauktwnwsqbyfdpsrq.supabase.co"
            # self.SUPABASE_KEY = ""
            self.BUCKET_NAME = "user-upload"
            self.ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.docx'}
        
    def allowed_file(self, filename):
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.ALLOWED_EXTENSIONS
    
    def upload(self):
    
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
    
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
    
        filename = file.filename
        if not self.allowed_file(filename):
            return jsonify({'error': 'File type not allowed.'}), 400
    
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = f"upload/{unique_filename}"
    
        try:
            supabase: Client = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)
            file_content = file.read()
            response = supabase.storage.from_(self.BUCKET_NAME).upload(file_path, file_content)
            # print("Supabase upload response:", response)
            if hasattr(response, "path") and response.path:
                return jsonify({'message': 'File uploaded successfully.', 'file_path': response.path}), 200
            else:
                # If the response has an 'error' attribute, show it; otherwise, generic error
                error_msg = getattr(response, "error", "Unknown error")
                return jsonify({'error': f"Upload failed: {error_msg}"}), 500
        except Exception as e:
            return jsonify({'error': f"Upload failed: {str(e)}"}), 500