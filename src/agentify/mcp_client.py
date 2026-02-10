import requests

class MCPClient:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint.rstrip("/")

    def list_tools(self) -> list[dict]:
        resp = requests.get(f"{self.endpoint}/tools")
        resp.raise_for_status()
        return resp.json().get("tools", [])

    def get_tool(self, name: str) -> dict:
        resp = requests.get(f"{self.endpoint}/tools/{name}")
        resp.raise_for_status()
        return resp.json()

    def invoke(self, name: str, arguments: dict):
        resp = requests.post(
            f"{self.endpoint}/tools/{name}/invoke",
            json={"arguments": arguments},
        )
        resp.raise_for_status()
        return resp.json()["result"]
