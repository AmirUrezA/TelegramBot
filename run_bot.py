#!/usr/bin/env python3
"""
Bot Runner Script
Simple script to run the enterprise Telegram bot
"""

import sys
import asyncio
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent))

from app.main import main

if __name__ == "__main__":
    print("🚀 Starting Enterprise Telegram Bot...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
