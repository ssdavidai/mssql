"""Test script for the HTTP server implementation."""
import asyncio
import aiohttp
import json
import os

async def test_http_server():
    """Test the HTTP server endpoints."""
    # Set test environment variables
    os.environ['MSSQL_SERVER'] = 'localhost'
    os.environ['MSSQL_DATABASE'] = 'testdb'
    os.environ['MSSQL_USER'] = 'sa'
    os.environ['MSSQL_PASSWORD'] = 'TestPassword123!'
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test GET request
        print("Testing GET /mcp...")
        async with session.get(f"{base_url}/mcp") as resp:
            print(f"Status: {resp.status}")
            data = await resp.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        
        # Test POST request - Initialize
        print("\nTesting POST /mcp (initialize)...")
        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            },
            "id": 1
        }
        async with session.post(f"{base_url}/mcp", json=payload) as resp:
            print(f"Status: {resp.status}")
            data = await resp.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        
        # Test tools/list
        print("\nTesting POST /mcp (tools/list)...")
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        async with session.post(f"{base_url}/mcp", json=payload) as resp:
            print(f"Status: {resp.status}")
            data = await resp.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        
        # Test with query parameters
        print("\nTesting GET /mcp with configuration...")
        config_url = f"{base_url}/mcp?server=myserver&database=mydb&user=myuser&password=mypass"
        async with session.get(config_url) as resp:
            print(f"Status: {resp.status}")
            data = await resp.json()
            print(f"Response: {json.dumps(data, indent=2)}")

if __name__ == "__main__":
    print("Starting HTTP server test...")
    print("Make sure to run the server first with: python -m mssql_mcp_server.http_server")
    asyncio.run(test_http_server())