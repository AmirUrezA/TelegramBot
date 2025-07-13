import psycopg2
from sqlalchemy import create_engine, text

# Database connection
DB_URL = "postgresql://postgres:amir@localhost:5432/mybot"
engine = create_engine(DB_URL)

try:
    with engine.connect() as conn:
        # Check existing tables
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        tables = [row[0] for row in result]
        print("✅ Tables created successfully:")
        for table in tables:
            print(f"  - {table}")
        
        # Check existing types
        result = conn.execute(text("""
            SELECT typname 
            FROM pg_type 
            WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            AND typtype = 'e';
        """))
        types = [row[0] for row in result]
        print(f"\n✅ Enum types created: {types}")
        
        expected_tables = ['products', 'users', 'orders', 'sellers', 'referral_codes']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            print(f"\n❌ Missing tables: {missing_tables}")
        else:
            print(f"\n🎉 All {len(expected_tables)} tables created successfully!")
            
except Exception as e:
    print(f"❌ Error connecting to database: {e}") 