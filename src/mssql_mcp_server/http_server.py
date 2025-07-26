"""HTTP server wrapper for Smithery deployment."""
import asyncio
import json
import logging
import os
from aiohttp import web
from mcp.server.stdio import AsyncStdioSession
from mcp import ClientCapabilities, InitializationOptions
from . import server
from urllib.parse import parse_qs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mssql_http_server")

class StreamableHTTPServer:
    """HTTP server that implements the Streamable HTTP protocol for MCP."""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        
    def setup_routes(self):
        """Set up HTTP routes."""
        self.app.router.add_get('/mcp', self.handle_mcp)
        self.app.router.add_post('/mcp', self.handle_mcp)
        self.app.router.add_delete('/mcp', self.handle_mcp)
        
    def parse_config_from_query(self, query_string: str) -> dict:
        """Parse configuration from query parameters using dot notation."""
        params = parse_qs(query_string)
        config = {}
        
        for key, values in params.items():
            # Skip reserved parameters
            if key in ['api_key', 'profile']:
                continue
                
            # Take the first value if multiple are provided
            value = values[0] if values else None
            if value is None:
                continue
                
            # Handle dot notation for nested objects
            parts = key.split('.')
            current = config
            
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
                
            # Set the value
            current[parts[-1]] = value
            
        return config
    
    def apply_config_to_env(self, config: dict):
        """Apply configuration to environment variables."""
        # Map configuration to environment variables
        mapping = {
            'server': 'MSSQL_SERVER',
            'database': 'MSSQL_DATABASE', 
            'user': 'MSSQL_USER',
            'password': 'MSSQL_PASSWORD',
            'port': 'MSSQL_PORT',
            'windowsAuth': 'MSSQL_WINDOWS_AUTH',
            'encrypt': 'MSSQL_ENCRYPT'
        }
        
        for key, env_var in mapping.items():
            if key in config:
                os.environ[env_var] = str(config[key])
                logger.info(f"Set {env_var} from configuration")
    
    async def handle_mcp(self, request: web.Request) -> web.Response:
        """Handle MCP requests."""
        logger.info(f"Received {request.method} request to /mcp")
        
        # Parse configuration from query parameters
        config = self.parse_config_from_query(request.query_string)
        logger.info(f"Parsed configuration: {json.dumps(config, indent=2)}")
        
        # Apply configuration to environment
        self.apply_config_to_env(config)
        
        if request.method == 'GET':
            # Return server information
            return web.json_response({
                "name": "mssql_mcp_server",
                "version": "0.1.0",
                "description": "Microsoft SQL Server MCP server",
                "capabilities": {
                    "tools": True,
                    "resources": True
                }
            })
            
        elif request.method == 'POST':
            # Handle MCP messages
            try:
                data = await request.json()
                logger.info(f"Received message: {data}")
                
                # Create a session and handle the message
                # This is a simplified implementation - you may need to manage sessions
                response = await self.process_mcp_message(data)
                
                return web.json_response(response)
                
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                return web.json_response(
                    {"error": str(e)},
                    status=500
                )
                
        elif request.method == 'DELETE':
            # Handle session cleanup
            return web.json_response({"status": "ok"})
            
    async def process_mcp_message(self, message: dict) -> dict:
        """Process an MCP message."""
        method = message.get("method")
        params = message.get("params", {})
        id = message.get("id")
        
        logger.info(f"Processing method: {method}")
        
        try:
            # Handle different MCP methods
            if method == "initialize":
                return {
                    "id": id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        },
                        "serverInfo": {
                            "name": "mssql_mcp_server",
                            "version": "0.1.0"
                        }
                    }
                }
                
            elif method == "initialized":
                return {"id": id, "result": {}}
                
            elif method == "tools/list":
                tools = await server.app.list_tools()
                return {
                    "id": id,
                    "result": {
                        "tools": [
                            {
                                "name": tool.name,
                                "description": tool.description,
                                "inputSchema": tool.inputSchema
                            }
                            for tool in tools
                        ]
                    }
                }
                
            elif method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments", {})
                result = await server.app.call_tool(name, arguments)
                return {
                    "id": id,
                    "result": {
                        "content": [
                            {"type": content.type, "text": content.text}
                            for content in result
                        ]
                    }
                }
                
            elif method == "resources/list":
                resources = await server.app.list_resources()
                return {
                    "id": id,
                    "result": {
                        "resources": [
                            {
                                "uri": str(resource.uri),
                                "name": resource.name,
                                "mimeType": resource.mimeType,
                                "description": resource.description
                            }
                            for resource in resources
                        ]
                    }
                }
                
            elif method == "resources/read":
                uri = params.get("uri")
                content = await server.app.read_resource(uri)
                return {
                    "id": id,
                    "result": {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "text/plain",
                                "text": content
                            }
                        ]
                    }
                }
                
            else:
                return {
                    "id": id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in process_mcp_message: {e}")
            return {
                "id": id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    def run(self):
        """Run the HTTP server."""
        port = int(os.environ.get('PORT', 8000))
        logger.info(f"Starting HTTP server on port {port}")
        web.run_app(self.app, host='0.0.0.0', port=port)

def main():
    """Main entry point."""
    server = StreamableHTTPServer()
    server.run()

if __name__ == "__main__":
    main()