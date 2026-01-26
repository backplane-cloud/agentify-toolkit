from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

from pathlib import Path
import uvicorn

from ..agents import create_agent

app = FastAPI()

# global state container
app.state.agents = {}  # name -> Agent instance

ui_path = Path(__file__).resolve().parents[1] / "ui"
app.mount("/ui", StaticFiles(directory=ui_path), name="ui")

@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Home page - show list of available agents with links to their chat interfaces.
    """
    HTML_PATH = Path(__file__).parent.parent / "ui" / "agent_list.html"
    
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    if not app.state.agents:
        tagline = "No agents currently loaded"
        agent_cards = """
        <div class="empty-state">
            <div class="empty-state-icon">🤖</div>
            <div class="empty-state-title">No Agents Available</div>
            <p class="empty-state-text">
                Deploy agents using: <code>agentify deploy &lt;agent.yaml&gt;</code>
            </p>
        </div>
        """
    else:
        tagline = f"Available Agents ({len(app.state.agents)})"
        agent_cards = ""

        for agent_id, agent in app.state.agents.items():
            name = getattr(agent, 'name', agent_id)
            description = getattr(agent, 'description', 'No description provided')
            provider = getattr(agent, 'provider', 'unknown')
            model_id = getattr(agent, 'model_id', 'unknown')
            role = getattr(agent, 'role', None)
            status = getattr(agent, 'status', 'stopped')

            agent_cards += f"""
            <div class="agent-row">
            <div class="agent-main">
                <div class="agent-name">🤖 {name}</div>
                <div class="agent-desc">{description}</div>
                <div class="agent-meta">
                <span class="meta-item">provider: <code>{provider}</code></span>
                <span class="meta-item">model: <code>{model_id}</code></span>
                {f'<span class="meta-item">role: <code>{role}</code></span>' if role else ''}
                </div>
            </div>

            <div class="agent-side">
                <span class="status-badge status-running">Running</span>
                <button class="agent-action" onclick="window.location='/agents/{agent_id}/chat'">chat</button>
                <button class="agent-action danger" hx-delete="/agents/{agent_id}/terminate" hx-swap="delete">delete</button>
            </div>
            </div>
            """

    # inject into template
    html_content = html_content.replace("{{TAGLINE}}", tagline)
    html_content = html_content.replace("{{AGENT_CARDS}}", agent_cards)

    return HTMLResponse(content=html_content)


@app.get("/agents/{agent_name}/chat", response_class=HTMLResponse)
async def agent_chat_ui(agent_name: str):
    """
    Serve the chat UI for a specific agent.
    """
    # Check if agent exists
    agent = app.state.agents.get(agent_name)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found"
        )
    
    HTML_PATH = Path(__file__).parent.parent / "ui" / "runtime_chat.html"
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Replace ALL template variables
    html_content = html_content.replace("{{AGENT_NAME}}", agent.name.upper())
    html_content = html_content.replace("{{AGENT_NAME_LOWER}}", agent_name)  # Add this line
    html_content = html_content.replace("{{AGENT_MODEL_ID}}", getattr(agent, "model_id", "Unknown"))
    html_content = html_content.replace("{{AGENT_PROVIDER}}", getattr(agent, "provider", "Unknown"))
    
    return HTMLResponse(content=html_content)

@app.get("/agents")
async def list_agents_endpoint():
    """
    List all loaded agents in the runtime.
    """
    agents_data = []

    for name, agent in app.state.agents.items():
        agents_data.append({
            "name": agent.name,
            "description": getattr(agent, "description", ""),
            "role": getattr(agent, "role", ""),
            "model": getattr(agent, "model_id", None),
            "provider": getattr(agent, "provider", None),
        })

    return {"agents": agents_data}


@app.post("/agents/{agent_name}/ask", response_class=HTMLResponse)
async def ask_agent(agent_name: str, question: str = Form(...)):
    """
    Handle chat message for a specific agent.
    """
    agent = app.state.agents.get(agent_name)
    if not agent:
        return HTMLResponse(
            content=f"<div class='error'>Agent '{agent_name}' not found.</div>",
            status_code=404
        )
    
    prompt = f"Answer with this role:{agent.role} the question: {question}"
    
    try:
        answer = agent.run(prompt)
    except Exception as e:
        answer = f"Agent error: {str(e)}"

    html = f"""
    <div class="message">
        <span class="agent"><strong>{agent.name}</strong>:</span> {answer}
    </div>
    """
    return HTMLResponse(content=html)

@app.post("/agents/{agent_name}/prompt")
async def prompt_agent(agent_name: str, request: Request):
    agent = app.state.agents.get(agent_name)
    if not agent:
        return JSONResponse({"error": f"Agent '{agent_name}' not found"}, status_code=404)

    body = await request.json()
    question = body.get("question")

    prompt = f"Answer with this role:{agent.role} the question:{question}"
    answer = agent.run(prompt)

    return {"answer": answer}


@app.post("/agents/add")
async def deploy_agents(request: Request):
    body = await request.json()
    agents = body.get("agents", [])

    loaded = []
    for spec in agents:
        name = spec.get("name")
        if not name:
            continue

        # TODO: create Agent from spec (you already have create_agent() in CLI)
        agent = create_agent(spec)
        app.state.agents[name] = agent
        loaded.append(name)

    return JSONResponse({"loaded": loaded})
    
@app.delete("/agents/{agent_name}/terminate")
async def remove_agent(agent_name: str):
    """Remove/unload an agent from the runtime by name."""
    # First, try direct key lookup
    if agent_name in app.state.agents:
        del app.state.agents[agent_name]
        return JSONResponse({"removed": agent_name, "success": True})
                            

    # If not found, try finding by agent.name attribute
    for key, agent in app.state.agents.items():
        if agent.name == agent_name:
            del app.state.agents[key]
            return JSONResponse({"removed": agent_name, "success": True})
    
    # Not found either way
    return JSONResponse(
        {"error": f"Agent '{agent_name}' not found"},
        status_code=404
    )

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*40)
    print("Agentify Runtime Server is now running!")
    print("Click or copy this link: http://127.0.0.1:8001")
    print("="*40 + "\n")

def start_runtime(port=None):
    """
    Start Agent Runtime
    """
    # app.state.agent = agent
    # app.state.agent_name = agent.name
    # app.state.provider = agent.provider
    # app.state.model_id = agent.model_id

    host="127.0.0.1"

    if port is None:
        port = 8001
    uvicorn.run(app, host=host, port=port)
