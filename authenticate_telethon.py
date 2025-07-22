# Step 1: Create a separate script to authenticate Telethon
# Save this as: authenticate_telethon.py

import asyncio
from telethon import TelegramClient
import os
from dotenv import load_dotenv
from telethon.tl.types import InputPeerUser
from telethon.errors import PeerFloodError
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerChannel
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import InviteToChannelRequest

load_dotenv()

async def setup_telethon_session():
    """
    Run this script ONCE on your local machine to create the session file
    """
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    
    print("Starting Telethon authentication...")
    print("Make sure you have your phone number ready to receive SMS")
    
    # Create client with the same session name you'll use in your bot
    client = TelegramClient('resume_session', API_ID, API_HASH)
    
    # This will prompt for phone number and SMS code
    await client.start()
    
    print("✅ Authentication successful!")
    
    # Test the connection
    me = await client.get_me()
    print(f"Logged in as: {me.first_name} {me.last_name or ''}")
    
    # Test sending a message to yourself
    await client.send_message('me', '🎉 Telethon session created successfully!')
    print("✅ Test message sent to 'Saved Messages'")
    
    # Test sending to the target username
    try:
        await client.send_message('@Arshya_Alaee', 'Test message from bot session')
        print("✅ Test message sent to @Arshya_Alaee")
    except Exception as e:
        print(f"❌ Failed to send to @Arshya_Alaee: {e}")
        print("Make sure the username exists and you can message them")
    
    await client.disconnect()
    print("Session saved as 'resume_session.session'")
    print("Copy this file to your bot's directory")

if __name__ == "__main__":
    asyncio.run(setup_telethon_session())

