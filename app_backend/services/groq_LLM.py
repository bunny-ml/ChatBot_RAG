import os
import json
from groq import Groq
import redis


redis_url = os.getenv("REDIS_URL")
groq_key = os.getenv("GROQ_KEY")


REDIS_URL = os.environ.get("REDIS_URL", redis_url)
redis_client = redis.from_url(REDIS_URL)

client = Groq(api_key=groq_key)

MAX_HISTORY = 20


def llm_response(user_id , user_query , context_data=None):
    
    history_key = f"chat_history:{user_id}"
    
    # Retrieve the conversation history from Redis
    raw_history = redis_client.lrange(history_key, 0, -1)
    chat_history = "\n".join(msg.decode("utf-8") for msg in reversed(raw_history)) if raw_history else ""

    if context_data:
        system_content=("""You are Peter, a helpful assistant.  
                            Hold a friendly, continuous conversation as if you naturally remember what was said earlier.  
                            Base every response strictly on the provided context — do not use any outside information.
                            you have full access to the files user upload.   
                            If the answer is not in the context, respond with: "Can you tell what exactly you are looking for!"  
                            Introduce yourself only in your very first message, and do not greet repeatedly or comment on the flow of the conversation.  
                            Respond in a concise, natural, and human-like way while strictly staying within the given context.
                            """
                            ) 
        user_content = (f"Previous chats:\n{chat_history}\n\n" +
                        f"Context:\n{context_data}\n\n" + 
                        f"User Question:\n{user_query}"
                        )

    else:
        system_content =("""You are Peter, a helpful assistant. 
                            always consider what is in the previous cahts and answer according to the convesation tone.
                            Maintain a seamless, natural conversation without acknowledging breaks or previous sessions.  
                            Never reintroduce yourself, greet the user again, or recap what has already been said unless explicitly asked.  
                            Base all answers on the provided chat history if it is not in history use exteral sources. 
                            Keep replies concise, friendly, and human-like, but never include meta-comments about remembering past chats or the user returning.
                            """
                            )
        user_content = (f"Previous chats:\n{chat_history} \n\n" 
                        f"User Question:\n{user_query}"
                        )


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
          temperature=1,  # user to control randomness 1 = fully random 
          max_completion_tokens=1024,
          top_p=0.6,    # Instead of always picking the highest-probability word, it picks from the smallest group of words whose combined probabilities are ≥ top_p
          stream=False,   #used to send data in small chunks
          stop=None,    #string that can cause model to stop  
          )
        response = completion.choices[0].message.content  


        # Store this query & response in Redis (as a single entry)
        redis_client.lpush(history_key, f"User: {user_query}\nBot: {response}")
        redis_client.expire(history_key, ex=86400)
        redis_client.ltrim(history_key, 0, MAX_HISTORY - 1)     
        return response

    except Exception as e:
        print(f"[ERROR] API request failed: {e}")
        err_msg = str(e)
        return f"Error: {err_msg}"

    