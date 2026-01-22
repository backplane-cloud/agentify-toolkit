from .tool import Tool, Action

def create_tool(spec: dict) -> Tool:
    """
    Create a Tool object (with Action objects) from a tool spec dict.
    """
    # Build actions dict
    actions = {}
    for action_name, action_data in spec.get("actions", {}).items():
        actions[action_name] = Action(
            name=action_name,
            method=action_data.get("method", "GET"),
            path=action_data.get("path", ""),
            params=action_data.get("params", {})
        )
    
    # Create the Tool object
    tool = Tool(
        name=spec["name"],
        description=spec.get("description", ""),
        endpoint=spec.get("endpoint", ""),
        actions=actions,
        version=spec.get("version", "0.0.0")
    )
    
    return tool
