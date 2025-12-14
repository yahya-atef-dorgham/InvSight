"""
WebSocket connection handler for real-time inventory updates.
"""
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
import asyncio

from src.database.session import get_db
from src.api.middleware.auth import get_current_user
from src.api.middleware.tenant import get_tenant_id


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Map tenant_id -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, tenant_id: str):
        """Accept a WebSocket connection and add to tenant's connection set."""
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = set()
        self.active_connections[tenant_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, tenant_id: str):
        """Remove a WebSocket connection from tenant's connection set."""
        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].discard(websocket)
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def broadcast_to_tenant(self, tenant_id: str, message: dict):
        """Broadcast a message to all connections for a specific tenant."""
        if tenant_id not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[tenant_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.active_connections[tenant_id].discard(connection)
        
        if not self.active_connections[tenant_id]:
            del self.active_connections[tenant_id]


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time inventory updates.
    
    Clients connect to: ws://host/ws/inventory?token=<jwt_token>
    """
    tenant_id = None
    
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008, reason="Authentication required")
            return
        
        # Decode JWT token to get tenant_id
        from jose import jwt
        from src.config.settings import settings
        
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            tenant_id = str(payload.get("tenant_id"))
            if not tenant_id:
                await websocket.close(code=1008, reason="Invalid token")
                return
        except Exception as e:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        # Connect
        await manager.connect(websocket, tenant_id)
        
        # Send welcome message
        await manager.send_personal_message({
            "type": "connected",
            "message": "Connected to inventory updates",
            "tenant_id": tenant_id
        }, websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (ping/pong or other commands)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                # Handle ping
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    }, websocket)
                
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await manager.send_personal_message({
                    "type": "ping"
                }, websocket)
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if tenant_id:
            manager.disconnect(websocket, tenant_id)


async def broadcast_inventory_update(tenant_id: str, inventory_data: dict):
    """
    Broadcast inventory update to all connected clients for a tenant.
    
    Args:
        tenant_id: Tenant UUID as string
        inventory_data: Inventory update data to broadcast
    """
    message = {
        "type": "inventory_update",
        "data": inventory_data,
        "timestamp": asyncio.get_event_loop().time()
    }
    await manager.broadcast_to_tenant(tenant_id, message)
