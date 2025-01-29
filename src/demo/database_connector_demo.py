import pandas as pd
from faker import Faker
from helper.database_connector import DatabaseConnector

fake = Faker()

def generate_demo_data(num_rows=5):
    """Generate fake data for demonstration"""
    data = []
    for i in range(num_rows):
        data.append({
            'id': i + 1,
            'name': fake.name(),
            'email': fake.email(),
            'age': fake.random_int(min=18, max=90)
        })
    return data

def main():
    # Initialize the database connector
    db = DatabaseConnector()
    
    try:
        print("\n1. Drop existing table if any")
        print("-" * 50)
        try:
            db.execute_query("DROP TABLE IF EXISTS demo_users")
            print("Table dropped successfully")
        except Exception as e:
            print(f"Error dropping table: {e}")

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
        db.execute_query(create_table_query)
        print("Table created successfully")

        print("\n3. Insert multiple rows")
        print("-" * 50)
        demo_data = generate_demo_data()
        insert_query = """
        INSERT INTO demo_users (id, name, email, age) 
        VALUES (%s, %s, %s, %s)
        """
        for user in demo_data:
            db.execute_query(
                insert_query, 
                (user['id'], user['name'], user['email'], user['age'])
            )
        print("Inserted demo data successfully")

        print("\n4. Select all data")
        print("-" * 50)
        results = db.execute_query("SELECT * FROM demo_users")
        print("All users:")
        for row in results:
            print(row)

        print("\n5. Select with condition")
        print("-" * 50)
        results = db.execute_query(
            "SELECT * FROM demo_users WHERE age > %s",
            (25,)
        )
        print("Users over 25:")
        for row in results:
            print(row)

        print("\n6. Update data")
        print("-" * 50)
        db.execute_query(
            "UPDATE demo_users SET age = %s WHERE id = %s",
            (31, 1)
        )
        print("Updated user with ID 1")

        print("\n7. Verify update")
        print("-" * 50)
        results = db.execute_query("SELECT * FROM demo_users WHERE id = 1")
        print("Updated user record:")
        print(results[0])

        print("\n8. Delete specific records")
        print("-" * 50)
        db.execute_query(
            "DELETE FROM demo_users WHERE age < %s",
            (25,)
        )
        print("Deleted users younger than 25")

        print("\n9. Final data check")
        print("-" * 50)
        results = db.execute_query("SELECT * FROM demo_users ORDER BY id")
        print("Remaining users:")
        for row in results:
            print(row)

        print("\n10. Drop table")
        print("-" * 50)
        db.execute_query("DROP TABLE demo_users")
        print("Table dropped successfully")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close_connection()

if __name__ == "__main__":
    main()