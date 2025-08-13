# ChatBot_RAG

A powerful **Retrieval-Augmented Generation (RAG)** chatbot that leverages large language models to provide intelligent responses based on user-uploaded documents. The project combines LLMs, vector embeddings, cloud storage, authentication, and memory management to deliver a seamless chat experience.

---

## Features

- **LLM Integration:** Uses **GROQ API** with the model `llama-3.3-70b-versatile` for advanced language understanding and generation.  
- **Document Embedding:** Utilizes **Jina AI** to embed uploaded documents into vector representations.  
- **Authentication:** Powered by **Supabase** for secure user login, registration, and logout. Authentication is managed using **JWT tokens**.  
- **File Storage:** Files uploaded by users are temporarily stored in **Supabase Buckets** (50 MB free storage). Files are automatically deleted after conversion into vectors.  
- **Vector Database:** Stores vector embeddings in **pgvector** on Supabase for fast retrieval.  
- **Large File Handling:** Supports file chunking to manage and process large documents efficiently.  
- **Chatbot Memory:** Uses **Redis** to maintain chatbot memory across sessions.  
- **Supported File Types:** Only allows uploads of **PDF, DOCX, and TXT** files.  

---

## Architecture Overview

1. **User Interaction:** Users login/register and upload supported documents.
2. **File Handling:** Uploaded files are stored temporarily in Supabase Buckets.
3. **Chunking:** Large files are split into manageable chunks for embedding.
4. **Embedding:** Jina AI generates vector embeddings for each document chunk.
5. **Vector Storage:** Embeddings are stored in Supabase pgvector.
6. **LLM Query:** When users ask questions, GROQ API (`llama-3.3-70b-versatile`) retrieves relevant chunks and generates responses.
7. **Memory Management:** Redis is used to store conversation history and context for improved responses.
8. **Cleanup:** Original files are deleted from Supabase Buckets after vectorization.

---

## Tech Stack

| Component          | Technology / Service                   |
|-------------------|-----------------------------------------|
| LLM API            | GROQ (`llama-3.3-70b-versatile`)       |
| Embeddings         | Jina.ai(https://jina.ai/)                                |
| Authentication     | Supabase (JWT-based)                   |
| File Storage       | Supabase Buckets                       |
| Vector DB          | Supabase pgvector                      |
| Memory / Cache     | Redis                                  |
| Deployment         | Render                                 |
| Supported Files    | PDF, DOCX, TXT                         |

---

## Installation & Setup

1. Clone the repository:
    ```bash
    git clone git@github.com:bunny-ml/ChatBot_RAG.git
    cd ChatBot_RAG
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure environment variables:
    ```
    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_anon_or_service_key
    JWT_SECRET=your_secret
    ANON_KEY=supabase_anon_key
    GROQ_API_KEY=your_groq_api_key
    REDIS_URL=your_redis_url
    JINA_API_KEY=jina.ai_api_key
    ```

4. Run the application:
    ```bash
    python3 main.py
    ```

---

## Usage

- **Register/Login:** Create an account with gmail or login with existing credentials.
- **Upload File:** Upload PDF, DOCX, or TXT files.
- **Ask Questions:** Chat with the bot about your uploaded documents.
- **Memory:** Previous interactions are remembered through Redis for context-aware responses.
- **Automatic Cleanup:** Uploaded files are deleted once embeddings are stored.

---

## Limitations

- Only supports **PDF, DOCX, and TXT** files.  
- Supabase Buckets have a **50 MB free storage limit**, so large file uploads may need careful management.  
- Requires internet connection for LLM queries and cloud services.
- There is no password reset option. 
- There is also change password option and no profile page.
---

## Deployment

The project is deployed on **Render**, providing an accessible online chatbot interface.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for improvements or bug fixes.

---

## License

This project is licensed under the MIT License.  

---

## Contact

For questions or support, contact: [Gmail: abhishek.chaudhary.ml@gmail.com or on Github: https://github.com/bunny-ml]