#!/usr/bin/env python3
"""
SoulHub v1.1.0 - Real-Time Collaboration Module
================================================
Enables live coordination between AI agents via WebSockets + Redis

Features:
- WebSocket server for real-time messaging
- Redis pub/sub for scalable message broadcasting
- Live soul synchronization across AI Army
- Event streaming (discoveries, solutions, patterns)
- Real-time status dashboard

New Commands:
- soulhub serve       - Start WebSocket server
- soulhub connect     - Connect to real-time network
- soulhub broadcast   - Broadcast message to all agents
- soulhub listen      - Listen to real-time events
"""

import asyncio
import json
import click
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Set
import sys

# WebSocket support
try:
    import websockets
    from websockets.server import serve
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    click.echo("Warning: websockets not installed. Run: pip install websockets")

# Redis support (optional, falls back to in-memory)
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RealtimeHub:
    """Real-time collaboration hub for AI agents"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8766):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.redis_client: Optional[redis.Redis] = None
        self.agent_registry: Dict[str, Dict[str, Any]] = {}

    async def init_redis(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis pub/sub"""
        if REDIS_AVAILABLE:
            try:
                self.redis_client = await redis.from_url(redis_url)
                click.echo(f"Connected to Redis: {redis_url}")
            except Exception as e:
                click.echo(f"Redis not available, using in-memory: {e}")
                self.redis_client = None
        else:
            click.echo("Redis not installed, using in-memory broadcasting")

    async def register_agent(self, websocket, agent_data: Dict[str, Any]):
        """Register new agent"""
        agent_id = agent_data.get('agent_id', 'unknown')
        self.agent_registry[agent_id] = {
            'agent_id': agent_id,
            'location': agent_data.get('location', 'unknown'),
            'role': agent_data.get('role', 'agent'),
            'connected_at': datetime.utcnow().isoformat() + 'Z',
            'websocket': websocket
        }

        # Broadcast agent joined
        await self.broadcast({
            'type': 'agent_joined',
            'agent_id': agent_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'total_agents': len(self.agent_registry)
        })

    async def unregister_agent(self, websocket):
        """Unregister disconnected agent"""
        agent_id = None
        for aid, data in self.agent_registry.items():
            if data['websocket'] == websocket:
                agent_id = aid
                break

        if agent_id:
            del self.agent_registry[agent_id]
            await self.broadcast({
                'type': 'agent_left',
                'agent_id': agent_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'total_agents': len(self.agent_registry)
            })

    async def broadcast(self, message: Dict[str, Any], exclude: Optional[Set] = None):
        """Broadcast message to all connected agents"""
        exclude = exclude or set()

        # Use Redis pub/sub if available
        if self.redis_client:
            try:
                await self.redis_client.publish('soulhub:broadcast', json.dumps(message))
            except Exception as e:
                click.echo(f"Redis publish error: {e}")

        # Also send via WebSockets (for agents connected to this server)
        if self.clients:
            message_json = json.dumps(message)
            websockets_to_remove = set()

            for websocket in self.clients:
                if websocket not in exclude:
                    try:
                        await websocket.send(message_json)
                    except websockets.exceptions.ConnectionClosed:
                        websockets_to_remove.add(websocket)

            # Clean up closed connections
            self.clients -= websockets_to_remove

    async def handle_client(self, websocket, path):
        """Handle individual client connection"""
        self.clients.add(websocket)
        agent_id = None

        try:
            click.echo(f"New connection from {websocket.remote_address}")

            async for message in websocket:
                data = json.loads(message)
                message_type = data.get('type')

                if message_type == 'register':
                    await self.register_agent(websocket, data)
                    agent_id = data.get('agent_id')

                elif message_type == 'soul_update':
                    # Agent updated soul, broadcast to others
                    await self.broadcast({
                        'type': 'soul_sync_event',
                        'agent_id': data.get('agent_id'),
                        'soul_sections': data.get('soul_sections'),
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }, exclude={websocket})

                elif message_type == 'discovery':
                    # Agent discovered solution, broadcast immediately
                    await self.broadcast({
                        'type': 'discovery_event',
                        'agent_id': data.get('agent_id'),
                        'discovery': data.get('discovery'),
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    })

                elif message_type == 'pattern':
                    # Agent learned pattern, broadcast
                    await self.broadcast({
                        'type': 'pattern_event',
                        'agent_id': data.get('agent_id'),
                        'pattern': data.get('pattern'),
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    })

                elif message_type == 'error':
                    # Agent encountered error/pain point, broadcast
                    await self.broadcast({
                        'type': 'pain_point_event',
                        'agent_id': data.get('agent_id'),
                        'error': data.get('error'),
                        'solution': data.get('solution'),
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    })

                elif message_type == 'heartbeat':
                    # Keep-alive ping
                    await websocket.send(json.dumps({'type': 'pong'}))

        except websockets.exceptions.ConnectionClosed:
            click.echo(f"Connection closed: {websocket.remote_address}")
        except Exception as e:
            click.echo(f"Error handling client: {e}")
        finally:
            self.clients.discard(websocket)
            if agent_id:
                await self.unregister_agent(websocket)

    async def start_server(self):
        """Start WebSocket server"""
        if not WEBSOCKETS_AVAILABLE:
            click.echo("ERROR: websockets library not installed")
            click.echo("Install with: pip install websockets")
            return

        await self.init_redis()

        click.echo(f"\nSoulHub Real-Time Server v1.1.0")
        click.echo(f"WebSocket: ws://{self.host}:{self.port}")
        click.echo(f"Agents connected: 0")
        click.echo(f"\nWaiting for agents to connect...")
        click.echo(f"Press Ctrl+C to stop\n")

        async with serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever


class RealtimeClient:
    """Client for connecting to SoulHub real-time network"""

    def __init__(self, server_url: str, agent_id: str):
        self.server_url = server_url
        self.agent_id = agent_id
        self.websocket = None

    async def connect(self):
        """Connect to SoulHub server"""
        if not WEBSOCKETS_AVAILABLE:
            click.echo("ERROR: websockets library not installed")
            return

        try:
            self.websocket = await websockets.connect(self.server_url)

            # Register this agent
            await self.websocket.send(json.dumps({
                'type': 'register',
                'agent_id': self.agent_id,
                'location': 'localhost',
                'role': 'client'
            }))

            click.echo(f"Connected to SoulHub: {self.server_url}")
            click.echo(f"Agent ID: {self.agent_id}")

            return True
        except Exception as e:
            click.echo(f"Connection failed: {e}")
            return False

    async def listen(self):
        """Listen to real-time events"""
        if not self.websocket:
            click.echo("Not connected")
            return

        try:
            async for message in self.websocket:
                data = json.loads(message)
                event_type = data.get('type')

                if event_type == 'agent_joined':
                    click.echo(f"\n[AGENT JOINED] {data['agent_id']} (Total: {data['total_agents']})")

                elif event_type == 'agent_left':
                    click.echo(f"\n[AGENT LEFT] {data['agent_id']} (Total: {data['total_agents']})")

                elif event_type == 'soul_sync_event':
                    click.echo(f"\n[SOUL UPDATE] {data['agent_id']} synced soul")

                elif event_type == 'discovery_event':
                    click.echo(f"\n[DISCOVERY] {data['agent_id']}: {data.get('discovery')}")

                elif event_type == 'pattern_event':
                    click.echo(f"\n[PATTERN] {data['agent_id']}: {data.get('pattern')}")

                elif event_type == 'pain_point_event':
                    click.echo(f"\n[PAIN POINT] {data['agent_id']}: {data.get('error')}")
                    if data.get('solution'):
                        click.echo(f"  Solution: {data['solution']}")

        except websockets.exceptions.ConnectionClosed:
            click.echo("\nDisconnected from server")
        except Exception as e:
            click.echo(f"\nError: {e}")

    async def broadcast_message(self, message_type: str, content: Dict[str, Any]):
        """Broadcast a message to all agents"""
        if not self.websocket:
            click.echo("Not connected")
            return

        try:
            await self.websocket.send(json.dumps({
                'type': message_type,
                'agent_id': self.agent_id,
                **content
            }))
            click.echo(f"Broadcasted: {message_type}")
        except Exception as e:
            click.echo(f"Broadcast failed: {e}")

    async def close(self):
        """Close connection"""
        if self.websocket:
            await self.websocket.close()


# CLI Commands for Real-Time Features

@click.group(name='realtime')
def realtime_cli():
    """Real-time collaboration commands (v1.1.0)"""
    pass


@realtime_cli.command()
@click.option('--host', default='0.0.0.0', help='Server host')
@click.option('--port', default=8766, help='Server port')
@click.option('--redis-url', default='redis://localhost:6379', help='Redis URL')
def serve(host: str, port: int, redis_url: str):
    """Start SoulHub real-time server"""
    hub = RealtimeHub(host=host, port=port)

    try:
        asyncio.run(hub.start_server())
    except KeyboardInterrupt:
        click.echo("\n\nServer stopped")


@realtime_cli.command()
@click.option('--server', default='ws://localhost:8766', help='Server URL')
@click.option('--agent-id', prompt='Agent ID', help='Your agent identifier')
def connect(server: str, agent_id: str):
    """Connect to SoulHub real-time network"""
    async def run():
        client = RealtimeClient(server, agent_id)
        if await client.connect():
            click.echo("\nListening to real-time events... (Ctrl+C to stop)\n")
            await client.listen()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        click.echo("\n\nDisconnected")


@realtime_cli.command()
@click.option('--server', default='ws://localhost:8766', help='Server URL')
@click.option('--agent-id', required=True, help='Your agent identifier')
@click.argument('message')
def broadcast(server: str, agent_id: str, message: str):
    """Broadcast message to all agents"""
    async def run():
        client = RealtimeClient(server, agent_id)
        if await client.connect():
            await client.broadcast_message('discovery', {'discovery': message})
            await client.close()

    asyncio.run(run())


@realtime_cli.command()
@click.option('--server', default='ws://localhost:8766', help='Server URL')
@click.option('--agent-id', required=True, help='Your agent identifier')
def listen(server: str, agent_id: str):
    """Listen to real-time events from network"""
    async def run():
        client = RealtimeClient(server, agent_id)
        if await client.connect():
            click.echo("\nListening... (Ctrl+C to stop)\n")
            await client.listen()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        click.echo("\n\nStopped listening")


if __name__ == '__main__':
    realtime_cli()
