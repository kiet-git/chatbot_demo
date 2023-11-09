# api.py
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
import time
from chain import get_response, create_chain
from pydantic import BaseModel

app = FastAPI()

class Question(BaseModel):
    content: str = None

class ChatBot:
    def __init__(self):
        self.chain = create_chain()

    def get_answer(self, question):
        start_time = time.time()
        print("Received question:", question.content)
        response = get_response(self.chain, question.content)
        end_time = time.time()
        print("Received answer:", response["answer"])
        return {
            "answer": response["answer"],
            "chat_history": response["chat_history"],
            "time_taken": round(end_time - start_time, 2)
        }

chat_bot = ChatBot()

@app.post("/ask/")
async def ask(question: Question, chat_bot: ChatBot = Depends()):
    return chat_bot.get_answer(question)


