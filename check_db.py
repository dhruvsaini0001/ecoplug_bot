"""
Database Connection Checker
Quick script to verify MongoDB connectivity.
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from chatbot.core.config import get_settings

settings = get_settings()


def check_mongodb_connection():
    """Test MongoDB connection."""
    print("=" * 60)
    print("🔍 DATABASE CONNECTION CHECK")
    print("=" * 60)
    print()
    
    # Check configuration
    print("📋 Configuration:")
    print(f"  MongoDB URL: {settings.MONGODB_URL}")
    print(f"  Database Name: {settings.MONGODB_DB_NAME}")
    print()
    
    # Try to connect
    print("🔌 Testing connection...")
    client = None
    
    try:
        # Create client with short timeout
        client = MongoClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=3000  # 3 second timeout
        )
        
        # Try to ping
        client.admin.command('ping')
        
        # Connection successful
        print("✅ SUCCESS: MongoDB is connected!")
        print()
        
        # Get server info
        server_info = client.server_info()
        print("📊 Server Information:")
        print(f"  Version: {server_info.get('version', 'Unknown')}")
        print()
        
        # List databases
        db_list = client.list_database_names()
        print(f"📚 Available Databases: {', '.join(db_list)}")
        print()
        
        # Check if our database exists
        db_name = settings.MONGODB_DB_NAME
        if db_name in db_list:
            print(f"✅ Database '{db_name}' exists")
            db = client[db_name]
            collections = db.list_collection_names()
            if collections:
                print(f"📦 Collections: {', '.join(collections)}")
            else:
                print("📦 No collections yet (database is empty)")
        else:
            print(f"⚠️  Database '{db_name}' does not exist yet")
            print("   (It will be created automatically when first used)")
        
        print()
        print("=" * 60)
        print("✅ DATABASE STATUS: CONNECTED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("❌ FAILED: Cannot connect to MongoDB")
        print()
        print(f"Error: {str(e)}")
        print()
        print("💡 Troubleshooting:")
        print("  1. Make sure MongoDB is running:")
        print("     - Windows: Check Services > MongoDB Server")
        print("     - Command: net start MongoDB")
        print()
        print("  2. Check if MongoDB is installed:")
        print("     - Download: https://www.mongodb.com/try/download/community")
        print()
        print("  3. Or use cloud MongoDB Atlas:")
        print("     - https://www.mongodb.com/cloud/atlas")
        print()
        print("  4. Current mode: IN-MEMORY SESSIONS")
        print("     - The chatbot works without MongoDB")
        print("     - Sessions stored in memory (lost on restart)")
        print()
        print("=" * 60)
        print("❌ DATABASE STATUS: NOT CONNECTED")
        print("=" * 60)
        return False
        
    finally:
        if client:
            client.close()


def check_current_mode():
    """Check which session storage mode is active."""
    print()
    print("=" * 60)
    print("🔍 CURRENT SESSION STORAGE MODE")
    print("=" * 60)
    print()
    
    # Check which service is imported in main.py
    try:
        with open('chatbot/api/main.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'InMemorySessionService' in content and 'from ..services.session_service_inmemory' in content:
            print("📦 Mode: IN-MEMORY")
            print("  ✓ Fast and simple")
            print("  ✓ No database required")
            print("  ⚠  Sessions lost on server restart")
            print("  ⚠  Not suitable for multiple servers")
        elif 'SessionService' in content and 'from ..services.session_service import' in content:
            print("📦 Mode: MONGODB")
            print("  ✓ Persistent sessions")
            print("  ✓ Survives server restarts")
            print("  ✓ Works with multiple servers")
            print("  ⚠  Requires MongoDB running")
        else:
            print("⚠️  Unknown mode")
    except Exception as e:
        print(f"❌ Error checking mode: {e}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    # Run connection check
    check_mongodb_connection()
    
    # Show current mode
    check_current_mode()
