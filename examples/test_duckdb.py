import duckdb

def test_duckdb():
    """
    Test basic DuckDB functionality:
    - Create an in-memory database
    - Create a table
    - Insert data
    - Query data
    - Perform aggregations
    """
    try:
        # Connect to an in-memory DuckDB database
        con = duckdb.connect(':memory:')
        print("✓ Connected to DuckDB successfully")

        # Create a sample table
        con.execute("""
            CREATE TABLE users (
                id INTEGER,
                name VARCHAR,
                age INTEGER,
                city VARCHAR
            )
        """)
        print("✓ Created users table")

        # Insert sample data
        con.execute("""
            INSERT INTO users VALUES
            (1, 'Alice', 25, 'New York'),
            (2, 'Bob', 30, 'London'),
            (3, 'Charlie', 35, 'Paris'),
            (4, 'Diana', 28, 'Tokyo'),
            (5, 'Eve', 32, 'Sydney')
        """)
        print("✓ Inserted sample data")

        # Query all users
        result = con.execute("SELECT * FROM users").fetchall()
        print("✓ Queried all users:")
        for row in result:
            print(f"  {row}")

        # Query with filtering
        result = con.execute("SELECT name, age FROM users WHERE age > 30").fetchall()
        print("✓ Users older than 30:")
        for row in result:
            print(f"  {row}")

        # Aggregation query
        result = con.execute("SELECT city, COUNT(*) as user_count FROM users GROUP BY city").fetchall()
        print("✓ Users per city:")
        for row in result:
            print(f"  {row}")

        # Test SQL functions
        result = con.execute("SELECT AVG(age) as avg_age, MAX(age) as max_age, MIN(age) as min_age FROM users").fetchall()
        print("✓ Age statistics:")
        print(f"  {result[0]}")

        # Close the connection
        con.close()
        print("✓ Connection closed successfully")

        return True

    except Exception as e:
        print(f"✗ DuckDB test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing DuckDB functionality...")
    success = test_duckdb()
    print("\nTest result:", "PASSED" if success else "FAILED")
    exit(0 if success else 1)