import pandas as pd
from faker import Faker
from helper.database_engine import DatabaseEngine

fake = Faker()

def generate_demo_data(num_rows=5):
    """Generate fake data for demonstration"""
    data = {
        'id': range(1, num_rows + 1),
        'name': [fake.name() for _ in range(num_rows)],
        'email': [fake.email() for _ in range(num_rows)],
        'age': [fake.random_int(min=18, max=90) for _ in range(num_rows)]
    }
    return pd.DataFrame(data)

def main():
    # Initialize the database engine
    db = DatabaseEngine()
    
    try:
        print("\n1. Delete existing table if any")
        print("-" * 50)
        try:
            db.delete_table("demo_users")
        except Exception as e:
            print(f"Table might not exist: {e}")

        print("\n2. Create new table")
        print("-" * 50)
        create_table_query = """
        CREATE TABLE demo_users (
            id INT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            age INT
        )
        """
        db.write_query(create_table_query)

        print("\n3. Insert data using DataFrame")
        print("-" * 50)
        demo_df = generate_demo_data()
        print("Generated data:")
        print(demo_df)
        db.write_dataframe(demo_df, "demo_users")

        print("\n4. Insert single row using write_query")
        print("-" * 50)
        db.write_query(
            "INSERT INTO demo_users (id, name, email, age) VALUES (:id, :name, :email, :age)",
            params={
                "id": 6,
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30
            }
        )

        print("\n5. Select all data")
        print("-" * 50)
        result_df = db.select_query("SELECT * FROM demo_users")
        print("All users:")
        print(result_df)

        print("\n6. Select with condition")
        print("-" * 50)
        result_df = db.select_query(
            "SELECT * FROM demo_users WHERE age > :min_age",
            params={"min_age": 25}
        )
        print("Users over 25:")
        print(result_df)

        print("\n7. Update data")
        print("-" * 50)
        rows_updated = db.update_query(
            "UPDATE demo_users SET age = :new_age WHERE name = :name",
            params={"new_age": 31, "name": "John Doe"}
        )
        print(f"Updated {rows_updated} rows")

        print("\n8. Verify update")
        print("-" * 50)
        result_df = db.select_query("SELECT * FROM demo_users WHERE name = 'John Doe'")
        print("Updated John Doe record:")
        print(result_df)

        print("\n9. Delete specific records")
        print("-" * 50)
        rows_deleted = db.delete_query(
            "DELETE FROM demo_users WHERE age < :age",
            params={"age": 25}
        )
        print(f"Deleted {rows_deleted} rows")

        print("\n10. Final data check")
        print("-" * 50)
        result_df = db.select_query("SELECT * FROM demo_users ORDER BY id")
        print("Remaining users:")
        print(result_df)

        print("\n11. Delete table")
        print("-" * 50)
        db.delete_table("demo_users")
        print("Demo completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.dispose_engine()

if __name__ == "__main__":
    main()