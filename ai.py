import google.generativeai as genai
from dotenv import load_dotenv
import os

# Create the model
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

class Ai:
  def __init__(self):
    GEMINI_API = os.getenv("GEMINI_API")
    genai.configure(api_key=GEMINI_API)
    self.generation_config = {
      "temperature": 1,
      "top_p": 0.95,
      "top_k": 40,
      "max_output_tokens": 8192,
      "response_mime_type": "text/plain",
    }

    self.model = genai.GenerativeModel(
      model_name="gemini-1.5-flash",
      generation_config=self.generation_config,
    )
    self.history = []
    self.chat_session = self.model.start_chat(
      history = self.history
    )
    
  def ai_resopnse(self,message: str)-> str:
    response = self.chat_session.send_message(message)
    return response.text
  
  def upload_to_gemini(self, path='./downloads/ss.jpg', mime_type=None):
        file = genai.upload_file(path, mime_type=mime_type)
        return file
  