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
- **Chatbot Memory:** Uses **Redis** to maintain chatbot memory across sessions (up to 10 previous interactions).  
- **Supported File Types:** Only allows uploads of **PDF, DOCX, and TXT** files.  

---

## Architecture Overview

1. **User Interaction:** Users register/login and upload supported documents.
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
|-------------------|---------------------------------------|
| LLM API            | GROQ (`llama-3.3-70b-versatile`)     |
| Embeddings         | [Jina.ai](https://jina.ai/)           |
| Authentication     | Supabase (JWT-based)                  |
| File Storage       | Supabase Buckets                       |
| Vector DB          | Supabase pgvector                     |
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
    SUPABASE_KEY=your_supabase_service_key
    JWT_SECRET=your_secret
    ANON_KEY=your_supabase_anon_key
    GROQ_API_KEY=your_groq_api_key
    REDIS_URL=your_redis_url
    JINA_API_KEY=your_jina_api_key
    ```

4. Run the application:
    ```bash
    python3 main.py
    ```

---

## Usage

- **Register/Login:** Create an account using Gmail or login with existing credentials.  
- **Upload File:** Upload '.txt', '.pdf', '.docx', '.doc', '.pptx', '.csv', '.xlsx' and '.md' files.  
- **Ask Questions:** Chat with the bot about your uploaded documents.  
- **Memory:** Previous interactions are remembered through Redis for context-aware responses (up to 20 interactions).  
- **Automatic Cleanup:** Uploaded files are deleted once embeddings are stored.  

---

## Limitations

- Only supports **'.txt', '.pdf', '.docx', '.doc', '.pptx', '.csv', '.xlsx' and '.md'** files.  
- Supabase Buckets have a **50 MB free storage limit**, so large file uploads may need careful management.  
- Requires internet connection for LLM queries and cloud services.  
- Password reset option is not available.  
- Change password functionality exists and there is no user profile page.  

---

## Deployment

The project is deployed on **Render**, providing an accessible online chatbot interface.  

**Live Demo:** [https://chatbot-rag-nwk5.onrender.com/](https://chatbot-rag-nwk5.onrender.com/)

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for improvements or bug fixes.

---

## Contact

For questions or support:  
- Gmail: abhishek.chaudhary.ml@gmail.com  
- GitHub: [https://github.com/bunny-ml](https://github.com/bunny-ml)
