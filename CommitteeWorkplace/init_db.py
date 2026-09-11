from database import init_database, insert_dummy_data

if __name__ == "__main__":
    print("🚀 Initializing Committee Workplace Database...")
    init_database()
    insert_dummy_data()
    print("✅ Database setup complete!")