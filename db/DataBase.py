import psycopg2
from psycopg2 import pool, Error
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager


class Database:
    """
    PostgreSQL Database connection and query execution handler
    """

    def __init__(self, host: str, port: int, database: str, user: str, password: str, min_conn: int = 1, max_conn: int = 3):
        """
        Initialize database connection pool

        Args:
            host: Database host address
            port: Database port (default: 5432)
            database: Database name
            user: Database user
            password: Database password
            min_conn: Minimum number of connections in pool
            max_conn: Maximum number of connections in pool
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

        try:
            # Create connection pool
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                min_conn,
                max_conn,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )

            if self.connection_pool:
                print(f"✓ Database connection pool created successfully")
                print(f"  Host: {self.host}:{self.port}")
                print(f"  Database: {self.database}")
        except (Exception, Error) as error:
            print(f"✗ Error creating connection pool: {error}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Context manager to get a connection from the pool

        Usage:
            with db.get_connection() as conn:
                # use connection
        """
        connection = None
        try:
            connection = self.connection_pool.getconn()
            yield connection
        except (Exception, Error) as error:
            if connection:
                connection.rollback()
            raise error
        finally:
            if connection:
                self.connection_pool.putconn(connection)

    @contextmanager
    def get_cursor(self, commit: bool = False):
        """
        Context manager to get a cursor from the pool

        Args:
            commit: Whether to auto-commit after cursor operations

        Usage:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO ...")
        """
        with self.get_connection() as connection:
            cursor = connection.cursor()
            try:
                yield cursor
                if commit:
                    connection.commit()
            except (Exception, Error) as error:
                connection.rollback()
                raise error
            finally:
                cursor.close()

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dictionaries

        Args:
            query: SQL SELECT query
            params: Query parameters (use %s placeholders in query)

        Returns:
            List of dictionaries with column names as keys

        Example:
            results = db.execute_query("SELECT * FROM users WHERE id = %s", (1,))
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)

                # Get column names from cursor description
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                # Fetch all results
                rows = cursor.fetchall()

                # Convert to list of dictionaries
                results = [dict(zip(columns, row)) for row in rows]

                return results
        except (Exception, Error) as error:
            print(f"✗ Error executing query: {error}")
            raise

    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query

        Args:
            query: SQL query (INSERT, UPDATE, DELETE)
            params: Query parameters (use %s placeholders in query)

        Returns:
            Number of rows affected

        Example:
            rows_affected = db.execute_update(
                "UPDATE users SET name = %s WHERE id = %s",
                ("John Doe", 1)
            )
        """
        try:
            with self.get_cursor(commit=True) as cursor:
                cursor.execute(query, params)
                rows_affected = cursor.rowcount
                return rows_affected
        except (Exception, Error) as error:
            print(f"✗ Error executing update: {error}")
            raise

    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute the same query multiple times with different parameters

        Args:
            query: SQL query
            params_list: List of parameter tuples

        Returns:
            Total number of rows affected

        Example:
            db.execute_many(
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                [("Alice", "alice@example.com"), ("Bob", "bob@example.com")]
            )
        """
        try:
            with self.get_cursor(commit=True) as cursor:
                cursor.executemany(query, params_list)
                rows_affected = cursor.rowcount
                return rows_affected
        except (Exception, Error) as error:
            print(f"✗ Error executing batch query: {error}")
            raise

    def execute_raw(self, query: str, params: Optional[Tuple] = None, fetch: bool = True) -> Optional[List[Tuple]]:
        """
        Execute a raw SQL query and return raw results

        Args:
            query: SQL query
            params: Query parameters
            fetch: Whether to fetch and return results

        Returns:
            List of tuples (raw results) if fetch=True, otherwise None

        Example:
            raw_results = db.execute_raw("SELECT id, name FROM users")
        """
        try:
            with self.get_cursor(commit=not fetch) as cursor:
                cursor.execute(query, params)

                if fetch:
                    return cursor.fetchall()
                else:
                    return None
        except (Exception, Error) as error:
            print(f"✗ Error executing raw query: {error}")
            raise

    def execute_transaction(self, queries: List[Tuple[str, Optional[Tuple]]]) -> bool:
        """
        Execute multiple queries in a transaction
        All queries succeed or all are rolled back

        Args:
            queries: List of (query, params) tuples

        Returns:
            True if transaction succeeded, raises exception otherwise

        Example:
            db.execute_transaction([
                ("INSERT INTO users (name) VALUES (%s)", ("Alice",)),
                ("UPDATE accounts SET balance = balance - 100 WHERE user_id = %s", (1,))
            ])
        """
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                try:
                    for query, params in queries:
                        cursor.execute(query, params)
                    connection.commit()
                    cursor.close()
                    return True
                except (Exception, Error) as error:
                    connection.rollback()
                    cursor.close()
                    raise error
        except (Exception, Error) as error:
            print(f"✗ Error executing transaction: {error}")
            raise

    def test_connection(self) -> bool:
        """
        Test if database connection is working

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    print("✓ Database connection test successful")
                    return True
                return False
        except (Exception, Error) as error:
            print(f"✗ Database connection test failed: {error}")
            return False

    def close_all_connections(self):
        """
        Close all connections in the pool
        Call this when shutting down the application
        """
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✓ All database connections closed")

    def __del__(self):
        """Destructor to ensure connections are closed"""
        if hasattr(self, 'connection_pool') and self.connection_pool:
            self.connection_pool.closeall()
