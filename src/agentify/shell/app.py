from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, Log, Input, Static, TextArea, Button, DirectoryTree
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual import events
from rich.panel import Panel
from rich.text import Text
from pathlib import Path

# Load Button
from textual.screen import ModalScreen
from textual import on
import os


from textual.binding import Binding
from textual.widgets import DataTable
from textual.widgets import Button





AGENTS_DIR = Path("examples/agents")

import yaml
from pathlib import Path

def get_yaml_type(path: Path) -> str:
    """Return 'agent' or 'tool' based on YAML content."""
    path = Path(path)  # ensure Path
    if not path.exists() or not path.is_file():
        return "unknown"

    try:
        with open(path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)

        if not isinstance(spec, dict):
            return "unknown"

        if "model" in spec or "role" in spec:
            return "agent"
        if "actions" in spec:
            return "tool"

    except Exception as e:
        # optional: print(e) to debug
        return "unknown"

    return "unknown"

class CreateAgentModal(ModalScreen):
    """Modal window to create a new agent."""

    def compose(self):
        yield Vertical(
            Static("Create New Agent"),
            Input(placeholder="Agent Name", id="agent_name"),
            Input(placeholder="Description", id="agent_description"),
            Input(placeholder="Model Provider", id="agent_provider"),
            Input(placeholder="Model ID", id="agent_model_id"),
            Input(placeholder="API Key Env Var", id="agent_api_key"),
            Input(placeholder="Role", id="agent_role"),
            Horizontal(
                Button("Create", id="create_button", variant="success"),
                Button("Cancel", id="cancel_button", variant="error")
            ),
            id="create_agent_form",
        )

    @on(Button.Pressed, "#create_button")
    def create_agent_pressed(self, event):
        """Collect input values and dismiss modal with result dict."""
        agent_data = {
            "name": self.query_one("#agent_name", Input).value.strip(),
            "description": self.query_one("#agent_description", Input).value.strip(),
            "model": {
                "provider": self.query_one("#agent_provider", Input).value.strip(),
                "id": self.query_one("#agent_model_id", Input).value.strip(),
                "api_key_env": self.query_one("#agent_api_key", Input).value.strip(),
            },
            "role": self.query_one("#agent_role", Input).value.strip(),
        }

        # Dismiss modal, return agent_data
        self.dismiss(agent_data)

    @on(Button.Pressed, "#cancel_button")
    def cancel(self, event):
        self.dismiss(None)

class DirectoryPicker(ModalScreen[str]):
    """Modal directory selector."""
    

    def compose(self):
        yield Vertical(
            Static("Select Agent Folder"),
            DirectoryTree(str(Path.cwd()), id="dir_tree"),
            id="dialog",
        )

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected):
        self.dismiss(event.path)


class AgentifyApp(App):
    """Agentify Operator Console"""
    TITLE = "Agentify Workbench"
    CSS_PATH = "css/styles.css"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("t", "toggle_dark", "Theme", show=True, priority=True),
        Binding("b", "toggle_left", "Toggle Agents", show=True),
    ]
    session_total = reactive(0)
    current_agents_dir = reactive(Path("examples/agents"))

    async def action_toggle_left(self):
        left = self.query_one("#left")

        if left.styles.display == "none":
            left.styles.display = "block"
        else:
            left.styles.display = "none"

    def action_toggle_dark(self):
        self.dark = not self.dark

    token_count = reactive(0)
    is_running = reactive(False)
    current_agent = None


    
    async def on_tree_node_selected(self, event: Tree.NodeSelected):
        node = event.node
        if not node.data or node.data.is_dir():
            return

        # node.data is full Path
        await self.run_agent(node.data)
       

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        

        yield Horizontal(
            Vertical(
                Static("Agents", id="title_bar"), 
                Tree("Agents", id="agents_tree"),
                Button("📂 Browse", id="load_agents_button", variant="default", classes="full_width"),
                Button("CREATE", id="create_agent_button", variant="primary", classes="full_width"),
                id="left"
            ),
            Vertical(
                # Call stats below
                
                Vertical(
                    Static("Token Stats", id="title_bar"), 
                    Horizontal(
                        Static("In: 0", id="call_stats_input", expand=True),
                        Static("Out: 0", id="call_stats_output", expand=True),
                        Static("Total: 0", id="call_stats_total", expand=True),
                        Static("Session: 0", id="call_stats_session_total", expand=True),
                        Static("Cost: 0 USD", id="call_stats_cost", expand=True),   
                        id="stats"  
                    ),
                    id="stats_bar"
                ),
                
                # YAML editor (hidden by default, can toggle)
                Vertical(
                    Static("Agent YAML", id="title_bar"), 
                    TextArea(id="yaml_editor", language="yaml"),
                    id="yaml_window",
                ),
                # TextArea(id="yaml_editor", language="yaml"), 
                

                # Chat log, scrollable
                
                Vertical(
                    Static("Agent CHAT", id="title_bar"), 
                    Log(id="chat_log"),
                    id="chat_log_window",
                ),
                
                # Input row: Input + Send button
                Horizontal(
                    Input(placeholder="Type your prompt and press [Enter]", id="chat_input"),
                    Button("Send", id="send_button"),
                    id="input_row",
                ),

              
                id="center",
            ),
            Vertical(
                Static("Agent Metadata", id="title_bar"), 
                DataTable(id="metadata"),
                id="right",
            ),
            id="main",
        )

        yield Footer()
        
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send_button":
            input_widget = self.query_one("#chat_input", Input)
            prompt = input_widget.value.strip()
            await self._run_prompt(prompt)
            
    def on_mount(self):
        self.load_agents()
        self.dark = True
        self.query_one(Tree).focus()
        self.refresh_agents_tree(self.current_agents_dir)

    async def action_toggle_yaml_editor(self):
        editor = self.query_one("#yaml_editor", TextArea)
        chat_log = self.query_one("#chat_log", Log)

        # Toggle via style.display
        if editor.styles.display == "none":
            editor.styles.display = "block"
            chat_log.styles.display = "none"
        else:
            editor.styles.display = "none"
            chat_log.styles.display = "block"
            
    async def on_shutdown(self):
        if self.current_agent and hasattr(self.current_agent, "close"):
            await self.current_agent.close()

    @on(Button.Pressed, "#create_agent_button")
    def open_create_agent(self, event):
        self.push_screen(CreateAgentModal(), self.on_agent_created)

    def on_agent_created(self, agent_data: dict | None):
        """Callback after modal is dismissed."""
        if agent_data:
            # Save agent YAML to the current directory
            import yaml
            from pathlib import Path

            agent_dir = self.current_agents_dir
            agent_name = agent_data["name"] + ".yaml"
            agent_path = agent_dir / agent_name

            with open(agent_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(agent_data, f, sort_keys=False)

            # Refresh tree to show new agent
            self.refresh_agents_tree(agent_dir)
    
    @on(Button.Pressed, "#load_agents_button")
    async def action_load_agents(self):
        self.push_screen(DirectoryPicker(), self.on_directory_selected)

    def on_directory_selected(self, path: str | None):
        if path:
            self.current_agents_dir = Path(path)
            self.refresh_agents_tree(path)
            
    def load_agents(self):
        tree = self.query_one("#agents_tree", Tree)
        root = tree.root
        root.expand()

        if AGENTS_DIR.exists():
            for file in AGENTS_DIR.glob("*.yaml"):
                root.add_leaf(file.name)
        else:
            root.add_leaf("No agents directory found")

    async def run_agent(self, agent_path: Path):
        from agentify.agent import create_agent
        import yaml

        log = self.query_one("#chat_log", Log)
        right = self.query_one("#metadata", DataTable)

        log.clear()


        with open(agent_path, "r") as f:
            spec = yaml.safe_load(f)

        agent = create_agent(spec, agent_file=agent_path.resolve())
        self.current_agent = agent

        self.render_metadata()
        log.write(f"Agent Ready: {agent.name.title()}")

        self.render_yaml(spec)

    def render_metadata(self):
        # query the DataTable itself
        table = self.query_one("#metadata", DataTable)
        agent = self.current_agent

        if not agent:
            table.clear(columns=True)
            table.add_columns("Info")
            table.add_row("No agent loaded")
            return

        table.clear(columns=True)
        table.add_columns("Property", "Value")
        table.add_row("Name", agent.name)
        table.add_row("Version", agent.version)
        # table.add_row("Role", agent.role)
        table.add_row("Model", agent.model_id)
        table.add_row("Provider", agent.provider)
        table.add_row("Tools", ', '.join(agent.get_tools()) if agent.get_tools() else "None")
        table.add_row("Input Tokens", str(agent.input_tokens))
        table.add_row("Output Tokens", str(agent.output_tokens))
        table.add_row("Token Cost", f"${round(agent.token_cost, 7)}")

    def render_yaml(self, spec: dict):
        """
        Display the given agent spec in the YAML editor, hiding the chat log.
        """
        import yaml

        editor = self.query_one("#yaml_editor", TextArea)
        # chat_log = self.query_one("#chat_log", Log)
        # input_row = self.query_one("#chat_input", Input)

        # Convert Python dict to YAML string
        yaml_content = yaml.safe_dump(spec, sort_keys=False)

        # Update the editor
        editor.load_text(yaml_content)

        # editor.styles.display = "block"

        # Show YAML editor, hide chat log
        # editor.styles.display = "block"
        # chat_log.styles.display = "none"

        # Optionally disable chat input while editing
        # input_row.disabled = True
        
    async def on_input_submitted(self, event: Input.Submitted):
        await self._run_prompt(event.value.strip())



    def refresh_agents_tree(self, folder_path: Path):
        tree = self.query_one("#agents_tree", Tree)
        tree.clear()

        folder_path = Path(folder_path)
        root = tree.root

        root.label = Text(f"📁 {folder_path.name or folder_path}", style="bold")
        root.data = folder_path
        root.expand()

        self._populate_tree(root, folder_path)

        tree.refresh()



    def _populate_tree(self, node, path: Path):
        """Recursively populate tree with folders + YAML files."""
        for item in sorted(path.iterdir()):
            if item.is_dir():
                folder_node = node.add(
                    Text(f"📁 {item.name}", style="bold"),
                    data=item,
                )
                self._populate_tree(folder_node, item)

            elif item.suffix == ".yaml":
                yaml_type = get_yaml_type(item)
                if yaml_type == "agent":
                    icon = "🤖"
                    style = "bold cyan"
                elif yaml_type == "tool":
                    icon = "🛠️"
                    style = "bold green"
                else:
                    icon = "📄"
                    style = "white"

                node.add_leaf(
                    Text(f"{icon} {item.name}", style=style),
                    data=item,
                )
                
    async def _run_prompt(self, prompt: str):
        if not self.current_agent or not prompt:
            return

        input_widget = self.query_one("#chat_input", Input)
        log = self.query_one("#chat_log", Log)

        call_stats_input = self.query_one("#call_stats_input", Static)
        call_stats_output = self.query_one("#call_stats_output", Static)
        call_stats_total = self.query_one("#call_stats_total", Static)
        call_stats_session_total = self.query_one("#call_stats_session_total", Static)
        call_stats_cost = self.query_one("#call_stats_cost", Static)

        input_widget.value = ""
        log.write(f"\nYou: {prompt}\n")

        # Show thinking indicator
        thinking_message = "🤔 Agent is thinking..."
        log.write(thinking_message)
        log.scroll_end(animate=True)

        agent = self.current_agent

        import asyncio
        response = await asyncio.to_thread(agent.run, prompt)

        # Remove the "thinking..." line
        # Simplest: clear the last line and write actual response
        log.lines.pop()  # removes last line
        # log.write(f"Agent: {response["text"]}\n")
        log.scroll_end(animate=True)

        # Extract response text and tokens
        if isinstance(response, dict):
            text = response.get("text", "")
            in_tokens = response.get("input_tokens", 0)
            out_tokens = response.get("output_tokens", 0)
            total_tokens = in_tokens + out_tokens
            self.session_total += total_tokens
            token_cost = round(response.get("token_cost", 0),7)
        else:
            text = str(response)
            in_tokens = getattr(agent, "last_input_tokens", 0)
            out_tokens = getattr(agent, "last_output_tokens", 0)
            token_cost = getattr(agent, "token_cost", 0)

        log.write(f"\nAgent: {text}\n")
        # log.scroll_end()
        log.scroll_end(animate=True)

        # Update per-call token stats
        # call_stats.update(f"Input Tokens: {in_tokens} | Output Tokens: {out_tokens} | Cost: {token_cost} USD")
        call_stats_input.update(f"Input Tokens: {in_tokens}")
        call_stats_output.update(f"Output Tokens: {out_tokens}")
        call_stats_total.update(f"Total: {total_tokens}")
        call_stats_session_total.update(f"Session: {self.session_total}")
        call_stats_cost.update(f"Cost: {token_cost} USD")

        # Update total metadata
        self.render_metadata()
        
if __name__ == "__main__":
    AgentifyApp().run()