import os
import json
from groq import Groq

def read_api_key(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            # Adjust the key name here if different
            return data.get("API_KEY") or data.get("api_key") or ""
    except FileNotFoundError:
        raise FileNotFoundError(f"API key file not found at: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"API key file at {file_path} is not a valid JSON")

file_path = os.path.join(os.path.dirname(__file__), "api_key.json")
file_path = os.path.abspath(file_path)
# print(f"Path to key: {file_path}")

api_key = read_api_key(file_path)
if not api_key:
    raise ValueError("API key is missing or empty. Check your file content.")

client = Groq(api_key=api_key)


def llm_response(user_query , context_data=None):
  
    # print("[INFO] Sending request to Groq...")


    if context_data:
        system_content=("You are a helpful assistant and your name is Peter. Use the following context strictly to answer the user's question. "
                        "If the answer is not found in the context, say you don't know.") 
        user_content = f"Context:\n{context_data}\n\nQuestion:\n{user_query}"
    else:
        system_content = "You are a helpful assistant and your name is Peter. Answer the user's question as best as you can."
        user_content = user_query

    messages=[
        {"role": "system",
          "content": system_content
                
        },
        {
          "role": "user",
          "content": user_content
        }
      ]
    try:
        completion = client.chat.completions.create(
          model="llama-3.3-70b-versatile",
          messages=messages,
          temperature=0.6,  # user to control randomness 1 = fully random 
          max_completion_tokens=1024,
          top_p=0.8,    # Instead of always picking the highest-probability word, it picks from the smallest group of words whose combined probabilities are ≥ top_p
          stream=False,   #used to send data in small chunks
          stop=None,    #string that can cause model to stop  
          )
        response = completion.choices[0].message.content

        def generate_response():
            yield response
        return generate_response()



    except Exception as e:
        print(f"[ERROR] API request failed: {e}")
        err_msg = str(e)

        def error_gen():
            yield f"Error: {err_msg}"
    return error_gen()

    