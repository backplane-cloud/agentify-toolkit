import requests
import itertools
import uuid
import json

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

    def __init__(self, endpoint: str, name: str = None, use_uuid: bool = False):
        self.name = name or "ephemeral"
        self.endpoint = endpoint.rstrip("/")
        self._next_id = 1
        self._initialized = False


    def _get_request_id(self):
        if self.use_uuid:
            return str(uuid.uuid4())
        return next(_request_id_counter)

    def _rpc(self, method: str, params=None):

        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
}

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id,  # integer id
            "method": method,
            "params": params
        }

        self._next_id += 1  # increment for next request

        # response = requests.post(self.endpoint, json=payload, headers=headers, stream=False)
        # print(response.headers)
        # print(response.text)
        # response.raise_for_status()
        # data = response.json()

        # if "error" in data:
        #     raise Exception(f"MCP Error: {data['error']}")
        # return data.get("result")
        response = requests.post(
            self.endpoint,
            json=payload,
            headers=headers,
            stream=True  # must be True for SSE
        )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if content_type.startswith("text/event-stream"):
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith("data: "):
                    raw = line[len("data: "):]
                    message = json.loads(raw)

                    if "error" in message:
                        raise Exception(f"MCP Error: {message['error']}")

                    return message.get("result")
        else:
            data = response.json()
            if "error" in data:
                raise Exception(f"MCP Error: {data['error']}")
            return data.get("result")

    def initialize(self):
        """Call MCP server initialize method."""
        if self._initialized:
            return
        
        try: 
            response = self._rpc("initialize", {
                "protocolVersion": "2024-11-05",
                "clientInfo": {
                    "name": "agentify",
                    "version": "0.1.0"
                },
                "capabilities": {}
            })

            self._initialized = True

            return response
        except Exception:
            self._initialized = False
            raise
        


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
