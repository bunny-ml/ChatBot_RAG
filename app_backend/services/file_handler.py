from flask import request, jsonify
from app_backend.services.supabse_client import SupabaseClient
import os
import threading
import io
from PyPDF2 import PdfReader
import docx
import requests
import uuid
import re
import jwt  # Ensure PyJWT is installed: pip install pyjwt


class file_handler_service:
    def __init__(self):
        self.supabase_client = SupabaseClient()
        self.supabase = self.supabase_client.client
        self.BUCKET_NAME = "user-upload"
        self.ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.docx'}
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.jina_api_key = os.getenv('JINA_API_KEY')
        self.jwt_secret = os.getenv('JWT_SECRET')  # FIX 1

    @staticmethod
    def chunk_text(text, max_tokens=500, overlap=50):
        """Splits text into overlapping chunks of approximately max_tokens words."""
        text = re.sub(r'\s+', ' ', text).strip()
        words = text.split()

        chunks = []
        start = 0
        while start < len(words):
            end = min(start + max_tokens, len(words))
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            start += max_tokens - overlap
        return chunks

    def embed_text_chunks(self, text_chunk):
        """Generate embeddings using Jina AI's embedding API."""
        try:
            url = "https://api.jina.ai/v1/embeddings"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.jina_api_key}"
            }
            payload = {
                "input": [text_chunk],
                "model": "jina-embeddings-v3",
                "task": "retrieval.passage",
                "dimensions": 384
            }
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]
        except Exception as e:
            print(f"[JINA EMBEDDING ERROR] {e}")
            return None

    def allowed_file(self, filename):
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.ALLOWED_EXTENSIONS

    def retrieve_relevant_chunks(self, query, user_id, top_k=5):
        """Retrieve top_k most relevant text chunks from Supabase using pgvector similarity search."""
        try:
            query_embedding = self.embed_text_chunks(query)
            if not query_embedding:
                return []

            results = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_count": top_k,
                    "user_id": user_id
                }
            ).execute()

            if not results.data:
                return []

            return [match["text_chunk"] for match in results.data]
        except Exception as e:
            print(f"[RETRIEVAL ERROR] {e}")
            return []

    def process_file_and_embed(self, file_path, user_id, doc_id):
        """Download file, extract text, chunk, embed, store vectors, and auto-delete."""
        try:
            data = self.supabase.storage.from_(self.BUCKET_NAME).download(file_path)
        except Exception as e:
            print(f"Error downloading {file_path}: {e}")
            self._delete_direct(file_path)
            return False

        if not data:
            print(f"Failed to download {file_path}")
            self._delete_direct(file_path)
            return False

        _, ext = os.path.splitext(file_path)
        text = ""
        try:
            if ext.lower() == ".txt":
                text = data.decode("utf-8", errors="ignore")
            elif ext.lower() == ".pdf":
                reader = PdfReader(io.BytesIO(data))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            elif ext.lower() == ".docx":
                doc = docx.Document(io.BytesIO(data))
                text = "\n".join(para.text for para in doc.paragraphs)
            else:
                print("Unsupported file type")
                self._delete_direct(file_path)
                return False
        except Exception as e:
            print(f"Error extracting text: {e}")
            self._delete_direct(file_path)
            return False

        chunks = self.chunk_text(text, max_tokens=500, overlap=50)

        for idx, chunk in enumerate(chunks):
            emb = self.embed_text_chunks(chunk)
            if emb:
                try:
                    self.supabase.table("document_vectors").insert({
                        "id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "doc_id": doc_id,
                        "file_path": file_path,
                        "chunk_index": idx,
                        "embedding": emb,
                        "text_chunk": chunk
                    }).execute()
                except Exception as e:
                    print(f"Error inserting embedding into Supabase: {e}")

        self._delete_direct(file_path)
        return True

    def _delete_direct(self, file_path):
        """Delete a file directly from Supabase storage."""
        try:
            self.supabase.storage.from_(self.BUCKET_NAME).remove([file_path])
            print(f"Deleted {file_path} from storage.")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    def upload_with_auto_delete(self):
        """Upload a file, process it asynchronously, then auto delete."""
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if not self.allowed_file(file.filename):
            return jsonify({'error': "Invalid file type"}), 400
        
        token = request.cookies.get("access_token")
        if not token:
            return jsonify({"error": "Not logged in"}), 401
        
        try:
            decoded = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                audience="authenticated"
            )
            user_id = decoded.get("sub")
            if not user_id:
                return jsonify({"error": "Invalid token: user_id missing"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 403
        except jwt.InvalidTokenError as e:
            print(f"JWT InvalidTokenError: {e}")
            return jsonify({"error": "Invalid token"}), 403

        file_path = f"upload/{file.filename}"
        doc_id = str(uuid.uuid4())

        try:
            file_content = file.read()
            res = self.supabase.storage.from_(self.BUCKET_NAME).upload(file_path, file_content)

            if not hasattr(res, "error") or res.error is None:
                threading.Thread(
                    target=self.process_file_and_embed,
                    args=(file_path, user_id, doc_id)
                ).start()
                return jsonify({
                    "message": "File uploaded successfully and will be processed",
                    "file_path": file_path,
                    "doc_id": doc_id
                }), 200
            else:
                return jsonify({"error": f"Upload failed: {res.error}"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
