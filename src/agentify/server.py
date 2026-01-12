# web.py
from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from pathlib import Path
import uvicorn

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")
ui_path = Path(__file__).parent / "ui"

app.mount("/ui", StaticFiles(directory=ui_path), name="ui")

@app.get("/", response_class=HTMLResponse)
async def home():
    HTML_PATH = Path(__file__).parent / "ui" / "chat.html"
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    agent_name = getattr(app.state, "agent_name", "Agent").upper()
    agent_model_id = getattr(app.state, "model_id", "Agent")
    agent_provider = getattr(app.state, "provider", "Agent")
    html_content = html_content.replace("{{AGENT_NAME}}", agent_name)
    html_content = html_content.replace("{{AGENT_MODEL_ID}}", agent_model_id)
    html_content = html_content.replace("{{AGENT_PROVIDER}}", agent_provider)
    
    return HTMLResponse(content=html_content)

@app.post("/ask", response_class=HTMLResponse)
async def ask_agent(question: str = Form(...)):
    agent = app.state.agent

    question = f"Answer with this role:{agent.role} the question: {question}"
    try:
        answer = agent.run(question)
    except Exception:
        answer = "Agent is currently busy. Please try again in a few seconds."

    # answer = agent.run(question)

    # Append chat messages in HTML
    html = f"""
    <div class="message">
        <span class="agent"><strong>{agent.name}</strong>:</span> {answer}
    </div>
    """
    return HTMLResponse(content=html)

@app.post("/prompt")
async def prompt_agent(request: Request ):
    agent = app.state.agent

    # Parse JSON body
    body = await request.json()
    question = body.get("question", "")
    
    
    prompt = f"Answer with this role:{agent.role} the question: {question}"

    try:
        answer = agent.run(prompt)
    except Exception:
        answer = "Agent is currently busy. Please try again in a few seconds."

    return {"answer": answer}

def serve_agent(agent, host="127.0.0.1", port=None):
    """
    Run the web UI with the given agent.
    Stores the agent in app.state and starts uvicorn.
    """
    app.state.agent = agent
    app.state.agent_name = agent.name
    app.state.provider = agent.provider
    app.state.model_id = agent.model_id

    if port is None:
        port = 8001
    uvicorn.run(app, host=host, port=port)
