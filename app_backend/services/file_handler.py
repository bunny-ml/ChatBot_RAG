from flask import request, jsonify
from app_backend.services.supabse_client import SupabaseClient
import os
import threading
from Sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
import requests
import uuid

class file_handler_service:
    def __init__(self):
        self.supabase_client = SupabaseClient()
        self.supabase = self.supabase_client.client
        self.BUCKET_NAME = "user-upload"
        self.ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.docx'}
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')

    model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_text_chunks(text_chunk):
        try:
            embedding = model.encode(text_chunks).tolist()
            return embedding
        except Exception as e:
            print(f"Embedding Failed: {e}")
            return None

    def allowed_file(self, filename):
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.ALLOWED_EXTENSIONS
    
    def process_file_and_embed(self, file_path):
        data = self.supabase.storage.form_(self.BUCKET_NAME).download(file_path)
        if data is None:
            print(f"Failed to download {file_path} for processing")
            return False
        
        _, ext = os.path.splitext(file_path)
        text = ""
        try:
            if ext == ".txt":
                text = data.decode('utf-8')
            elif ext == '.pdf':
                reader = PdfReader(io.BytesIO(data))
                for page in reader.pages:
                    text += page.extract_text() + '\n'
            elif ext == '.docx':
                doc = docx.Document(io.BytesIO(data))
                text = '\n'.join([para.text for para in doc.paragraphs])
            else:
                print("Unsupported file extension")
                return False
        except Exception as e:
            print(f"error extracting text: {e}")
            return False
        
        chunks = chunk_test(text , max_token= 500 , overlap= 50)

        embeddings =[]
        for chunk in chunks:
            emebedding = embed_text_chunks(chunk)
            emebedding.append(emebedding)


        store_embeddings(emebeddings , metadata={'file_path': file_path})

        return True
    
    
    def upload_with_auto_delete(self):
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        filename = file.filename
        if not self.allowed_file(filename):
            allowed = ', '.join(self.ALLOWED_EXTENSIONS)
            return jsonify({'error': f"'{filename}' is not an accepted file type. Use one of : {allowed}"}), 400

        file_path = f"upload/{filename}"
        doc_id = str(uuid.uuid4())  # unique document ID
        # print(f"doc id: {doc_id}")

        try:
            file_content = file.read()
            response = self.supabase.storage.from_(self.BUCKET_NAME).upload(file_path, file_content)
            # print("[UPLOAD] Stored path:", response.path if hasattr(response, "path") else response)

            if hasattr(response, "path") and response.path:
                file_path = response.path

                threading.Thread(target=self._process_and_delete, args=(file_path,)).start()

                return jsonify({
                    'message': 'File uploaded successfully',
                    'file_path': file_path,
                    'doc_id': doc_id
                }), 200


                # COMMENT OUT for now to avoid auto deletion interfering with embedding
                # threading.Timer(30.0, self._delete_direct, args=[file_path]).start()

                # return jsonify({
                #     'message': 'File uploaded successfully.',
                #     'file_path': response.path,
                #     'doc_id': doc_id
                # }), 200
            else:
                error_msg = getattr(response, "error", "Unknown error")
                return jsonify({'error': f"Upload failed: {error_msg}"}), 500
        except Exception as e:
            return jsonify({'error': f"Upload failed: {str(e)}"}), 500

    def _process_and_delete(self, file_path):
            # 1. Process embedding
            success = self.process_file_and_embed(file_path)

            # 2. Delete file if embedding was successful
            if success:
                self._delete_direct(file_path)
            else:
                print(f"Embedding failed, file {file_path} not deleted.")
