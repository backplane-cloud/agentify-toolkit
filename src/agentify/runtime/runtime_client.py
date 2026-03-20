import requests

def list_agents(server_url):
    resp = requests.get(f"{server_url}/agents")
    resp.raise_for_status()
    return resp.json()

def upload_agent(server_url, yaml_file):
    files = {'file': open(yaml_file, 'rb')}
    resp = requests.post(f"{server_url}/agents", files=files)
    resp.raise_for_status()
    return resp.json()

def run_agent(server_url, yaml_file):
    files = {'file': open(yaml_file, 'rb')}
    resp = requests.post(f"{server_url}/agents/run", files=files)
    resp.raise_for_status()
    return resp.json()

def delete_agent(server_url, agent_name):
    resp = requests.delete(f"{server_url}/agents/{agent_name}")
    resp.raise_for_status()
    return resp.json()
