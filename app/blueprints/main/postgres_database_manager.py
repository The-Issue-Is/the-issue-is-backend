import logging
import psycopg2
from psycopg2 import Error
from dotenv import dotenv_values

environ = dotenv_values(".env")


class PostgresDatabaseManager:
    def __init__(self, database_host=None, database_port=None, database_user=None, database_password=None, database_name=None) -> None:
        self.database_host = database_host or environ['DATABASE_HOST']
        self.database_port = database_port or environ['DATABASE_PORT']
        self.database_user = database_user or environ['DATABASE_USER']
        self.database_password = database_password or environ['DATABASE_PASSWORD']
        self.database_name = database_name or environ['DATABASE_NAME']

    def _get_connection(self) -> psycopg2.extensions.connection:
        try:
            connection = psycopg2.connect(user=self.database_user,
                                          password=self.database_password,
                                          host=self.database_host,
                                          port=self.database_port,
                                          database=self.database_name)

            return connection
        except (Exception, Error) as error:
            logging.error("Error while connecting to PostgreSQL", error)

    def _execute_query(self, query: str, params: tuple) -> None:
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                connection.commit()
        except (Exception, Error) as error:
            logging.error("Database operation error", error)

    def _fetch_all(self, query: str, params: tuple) -> list:
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return [dict(zip([column[0] for column in cursor.description], row)) for row in result]
        except (Exception, Error) as error:
            logging.error("Database operation error", error)
            return []
        
    def _fetch_one(self, query: str, params: tuple) -> dict:
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return dict(zip([column[0] for column in cursor.description], result))
        except (Exception, Error) as error:
            logging.error("Database operation error", error)
            return {}
        
    def select_user_by_github_user_id(self, github_user_id: int) -> dict:
        query = """
            SELECT username, github_user_id, access_token, access_token_expires_in, refresh_token, refresh_token_expires_in
            FROM users
            WHERE github_user_id = %s
        """
        params = (github_user_id,)
        result = self._fetch_one(query, params)
        return result
        
    def insert_user(self, username: str, github_user_id: int, access_token: str, access_token_expires_in: int, refresh_token: str, refresh_token_expires_in: int ) -> None:
        query = """
            INSERT INTO users (username, github_user_id, access_token, access_token_expires_in, refresh_token, refresh_token_expires_in)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (username, github_user_id, access_token, access_token_expires_in, refresh_token, refresh_token_expires_in)
        self._execute_query(query, params)

    def update_user(self, github_user_id: int, access_token: str, access_token_expires_in: int, refresh_token: str, refresh_token_expires_in: int ) -> None:
        query = """
            UPDATE users
            SET access_token = %s, access_token_expires_in = %s, refresh_token = %s, refresh_token_expires_in = %s
            WHERE github_user_id = %s
        """
        params = (access_token, access_token_expires_in, refresh_token, refresh_token_expires_in, github_user_id)
        self._execute_query(query, params)

    def upsert_user_by_github_user_id(self, username: str, github_user_id: int, access_token: str, access_token_expires_in: int, refresh_token: str, refresh_token_expires_in: int ) -> None:
        query = """
            INSERT INTO users (username, github_user_id, access_token, access_token_expires_in, refresh_token, refresh_token_expires_in)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (github_user_id) DO UPDATE
            SET access_token = %s, access_token_expires_in = %s, refresh_token = %s, refresh_token_expires_in = %s
        """
        params = (username, github_user_id, access_token, access_token_expires_in, refresh_token, refresh_token_expires_in, access_token, access_token_expires_in, refresh_token, refresh_token_expires_in)
        self._execute_query(query, params)