from fastapi import FastAPI
from pydantic import BaseModel
from .utils import analyze_text

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/analyze")
def analyze(input: TextInput):
    return analyze_text(input.text)
