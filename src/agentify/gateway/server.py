from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agentify.providers.agentify import run_agentify

app = FastAPI(title="Agentify Model Gateway")

class ChatRequest(BaseModel):
    model: str
    prompt: str
    
class ChatResponse(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int

@app.post("/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest):

    try:
        output = run_agentify(
            model_id=req.model,
            user_prompt=req.prompt
        )

        return ChatResponse(**output)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
