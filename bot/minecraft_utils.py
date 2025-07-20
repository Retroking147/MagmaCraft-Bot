"""
Minecraft Server Utilities
"""
import asyncio
import logging
import socket
import struct
from typing import Tuple

logger = logging.getLogger(__name__)

async def check_minecraft_server(server_ip: str, server_port: int = 25565) -> Tuple[int, int, bool]:
    """
    Check Minecraft server status and get player count
    
    Args:
        server_ip (str): Server IP address
        server_port (int): Server port (default: 25565)
        
    Returns:
        Tuple[int, int, bool]: (current_players, max_players, is_online)
    """
    try:
        # Use asyncio to run the synchronous socket operation
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _sync_check_minecraft_server, server_ip, server_port)
        return result
    except Exception as e:
        logger.error(f"Error checking Minecraft server {server_ip}:{server_port}: {e}")
        return 0, 0, False

def _sync_check_minecraft_server(server_ip: str, server_port: int) -> Tuple[int, int, bool]:
    """
    Synchronous Minecraft server status check using Server List Ping protocol
    """
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        
        # Connect to server
        sock.connect((server_ip, server_port))
        
        # Send handshake packet (Protocol version 47, Server List Ping)
        handshake_data = _create_handshake_packet(server_ip, server_port)
        sock.send(handshake_data)
        
        # Send status request packet
        status_request = _create_status_request_packet()
        sock.send(status_request)
        
        # Read response
        response = _read_varint(sock)  # Packet length
        packet_id = _read_varint(sock)  # Packet ID (should be 0)
        
        if packet_id != 0:
            logger.warning(f"Unexpected packet ID: {packet_id}")
            return 0, 0, False
        
        # Read JSON response length and data
        json_length = _read_varint(sock)
        json_data = sock.recv(json_length).decode('utf-8')
        
        sock.close()
        
        # Parse JSON response
        import json
        server_info = json.loads(json_data)
        
        # Extract player information
        players = server_info.get('players', {})
        online = players.get('online', 0)
        max_players = players.get('max', 0)
        
        logger.info(f"Minecraft server {server_ip}:{server_port} - {online}/{max_players} players")
        return online, max_players, True
        
    except socket.timeout:
        logger.warning(f"Timeout connecting to Minecraft server {server_ip}:{server_port}")
        return 0, 0, False
    except socket.gaierror:
        logger.warning(f"Could not resolve hostname {server_ip}")
        return 0, 0, False
    except ConnectionRefusedError:
        logger.warning(f"Connection refused to {server_ip}:{server_port}")
        return 0, 0, False
    except Exception as e:
        logger.error(f"Error in sync Minecraft server check: {e}")
        return 0, 0, False

def _create_handshake_packet(server_ip: str, server_port: int) -> bytes:
    """Create Minecraft handshake packet"""
    # Protocol version (47 for 1.8.x, works with most servers)
    protocol_version = _pack_varint(47)
    
    # Server address
    server_address = server_ip.encode('utf-8')
    server_address_length = _pack_varint(len(server_address))
    
    # Server port
    server_port_bytes = struct.pack('>H', server_port)
    
    # Next state (1 for status)
    next_state = _pack_varint(1)
    
    # Build packet data
    packet_data = protocol_version + server_address_length + server_address + server_port_bytes + next_state
    
    # Add packet length and ID
    packet_length = _pack_varint(len(packet_data) + 1)  # +1 for packet ID
    packet_id = _pack_varint(0)  # Handshake packet ID is 0
    
    return packet_length + packet_id + packet_data

def _create_status_request_packet() -> bytes:
    """Create Minecraft status request packet"""
    packet_id = _pack_varint(0)  # Status request packet ID is 0
    packet_length = _pack_varint(len(packet_id))
    return packet_length + packet_id

def _pack_varint(value: int) -> bytes:
    """Pack integer as varint (Minecraft protocol format)"""
    data = b''
    while True:
        byte = value & 0x7F
        value >>= 7
        if value != 0:
            byte |= 0x80
        data += struct.pack('B', byte)
        if value == 0:
            break
    return data

def _read_varint(sock) -> int:
    """Read varint from socket"""
    value = 0
    position = 0
    while True:
        byte_data = sock.recv(1)
        if not byte_data:
            raise ConnectionError("Socket closed while reading varint")
        
        byte = struct.unpack('B', byte_data)[0]
        value |= (byte & 0x7F) << position
        
        if (byte & 0x80) == 0:
            break
            
        position += 7
        if position >= 32:
            raise ValueError("VarInt is too big")
    
    return value

async def update_minecraft_counter_channel(bot, channel_id: int, server_info: dict):
    """
    Update a Minecraft counter channel with current player count
    
    Args:
        bot: Discord bot instance
        channel_id: ID of the channel to update
        server_info: Dictionary containing server connection info
        
    Returns:
        Tuple[bool, bool]: (success, has_players)
    """
    try:
        # Get channel
        channel = bot.get_channel(channel_id)
        if not channel:
            logger.warning(f"Could not find channel {channel_id} for Minecraft counter")
            return False, False
        
        # Check server status
        player_count, max_players, is_online = await check_minecraft_server(
            server_info['server_ip'], 
            server_info['server_port']
        )
        
        # Format channel name based on channel type
        channel_type = server_info.get('channel_type', 'combined')  # Default to old behavior for compatibility
        
        if channel_type == 'status':
            # Status channel: show online/offline with emoji
            status_indicator = "🟢" if is_online else "🔴"
            status_text = "Online" if is_online else "Offline"
            formatted_name = server_info['channel_name_template'].format(status=f"{status_indicator} {status_text}")
        elif channel_type == 'count':
            # Count channel: show player count with person emoji
            if is_online:
                formatted_name = server_info['channel_name_template'].format(count=f"{player_count}/{max_players}")
            else:
                formatted_name = server_info['channel_name_template'].format(count="0/0")
        else:
            # Legacy combined format (for backward compatibility)
            if is_online:
                status_indicator = "🟢"
                formatted_name = server_info['channel_name_template'].format(count=f"{status_indicator} {player_count}/{max_players}")
            else:
                status_indicator = "🔴"
                formatted_name = server_info['channel_name_template'].format(count=f"{status_indicator} Offline")
        
        # Update channel name if it's different
        if channel.name != formatted_name:
            await channel.edit(name=formatted_name, reason="Minecraft player count update")
            logger.info(f"Updated Minecraft counter channel: {formatted_name}")
        
        # Return success and whether there are active players
        has_players = is_online and player_count > 0
        return True, has_players
        
    except Exception as e:
        logger.error(f"Error updating Minecraft counter channel {channel_id}: {e}")
        return False, False