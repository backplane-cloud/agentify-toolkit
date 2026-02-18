import requests
import itertools
import uuid


class MCPError(Exception):
    """Generic MCP error from server response."""

    def __init__(self, code, message, data=None):
        super().__init__(f"MCPError {code}: {message}")
        self.code = code
        self.message = message
        self.data = data


_request_id_counter = itertools.count(1)  # fallback integer IDs


class MCPClientHTTP:
    """
    Minimal MCP HTTP client (JSON-RPC 2.0) compatible with most MCP servers.
    """

    def __init__(self, endpoint: str, use_uuid: bool = False):
        self.endpoint = endpoint.rstrip("/")
        self._next_id = 1

    def _get_request_id(self):
        if self.use_uuid:
            return str(uuid.uuid4())
        return next(_request_id_counter)

    def _rpc(self, method: str, params=None):
        if params is None:
            params = {}

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id,  # integer id
            "method": method,
            "params": params
        }
        self._next_id += 1  # increment for next request

        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise Exception(f"MCP Error: {data['error']}")
        return data.get("result")

    def initialize(self):
        """Call MCP server initialize method."""
        return self._rpc("initialize", {})

    def list_tools(self):
        response = self._rpc("tools/list")
        if not response:
            return []
        if "tools" not in response:
            raise Exception(f"Invalid response from server: {response}")
        return response["tools"]

    def call_tool(self, name: str, arguments: dict = None):
        """Call a tool by name with optional arguments dict."""
        params = {"name": name}
        if arguments:
            params["arguments"] = arguments
        return self._rpc("tools/call", params)
    
    def register_tools(self, path: str):
        """Register a YAML tool or directory of tools on the MCP Server"""
        params = {"path": path}
        return self._rpc("tools/register", params)

    def deregister_tool(self, tool_name: str):
        """Deregister a registered tool from the MCP Server by name."""
        params = {"name": tool_name}
        return self._rpc("tools/deregister", params)
