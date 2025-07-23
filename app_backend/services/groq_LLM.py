import os
from groq import Groq

def read_api_key(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"API key file not found at: {file_path}")


def llm_response(user_query , context_data=None):

    api_key = read_api_key('/workspace/ChatBot_Backend-RAG-/app/services/api_key.json')
    client = Groq(api_key=api_key)
    if context_data:
        system_content=("You are a helpful assistant. Use the following context strictly to answer the user's question. "
                "If the answer is not found in the context, say you don't know.") 
        user_content = f"Context:\n{context_data}\n\nQuestion:\n{user_query}"
    else:
        system_content = "You are a helpful assistant. Answer the user's question as best as you can."
        user_content = user_query

    messages=[
        {
          "role": "system",
          "content": system_content
                
        },
        {
          "role": "user",
          "content": user_content
        }
      ],

    completion = client.chat.completions.create(
      model="llama-3.3-70b-versatile",
      temperature=0.6,  # user to control randomness 1 = fully random 
      max_completion_tokens=1024,
      top_p=0.8,    # Instead of always picking the highest-probability word, it picks from the smallest group of words whose combined probabilities are ≥ top_p
      stream=True,   #used to send data in small chunks
      stop=None,    #string that can cause model to stop  
      )

    def response_generate():
      for chunk in completion:
          response = chunk.choices[0].delta.content 
          if response:
            yield response
      yield '\n\nPlease feel free to connect with the creator, Abhishek :)'
    return response_generate()

    