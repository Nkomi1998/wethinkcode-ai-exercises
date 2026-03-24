# Database connection manager with complex initialization
from abc import ABC, abstractmethod

class DatabaseConnector(ABC):
    """Abstract base class for database connectors"""
    
    def __init__(self, config):
        self.config = config
    
    @abstractmethod
    def build_connection_string(self):
        """Build the connection string for this database type"""
        pass
    
    def connect(self):
        """Perform the actual connection"""
        connection_string = self.build_connection_string()
        print(f"Connecting to {self.config['db_type']} database...")
        print(f"{self.config['db_type'].capitalize()} Connection: {connection_string}")
        # In a real app, we would create the actual connection here
        return None

class MySQLConnector(DatabaseConnector):
    def build_connection_string(self):
        config = self.config
        connection_string = f"mysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        connection_string += f"?charset={config.get('charset', 'utf8')}"
        connection_string += f"&connectionTimeout={config.get('connection_timeout', 30)}"
        
        if config.get('use_ssl', False):
            connection_string += "&useSSL=true"
        
        return connection_string

class PostgreSQLConnector(DatabaseConnector):
    def build_connection_string(self):
        config = self.config
        connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        
        if config.get('use_ssl', False):
            connection_string += "?sslmode=require"
        
        return connection_string

class MongoDBConnector(DatabaseConnector):
    def build_connection_string(self):
        config = self.config
        connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        connection_string += f"?retryAttempts={config.get('retry_attempts', 3)}"
        connection_string += f"&poolSize={config.get('pool_size', 5)}"
        
        if config.get('use_ssl', False):
            connection_string += "&ssl=true"
        
        return connection_string

class RedisConnector(DatabaseConnector):
    def build_connection_string(self):
        config = self.config
        return f"{config['host']}:{config['port']}/{config['database']}"

class DatabaseConnectorFactory:
    """Factory for creating database connectors"""
    
    @staticmethod
    def create_connector(config):
        db_type = config['db_type']
        
        if db_type == 'mysql':
            return MySQLConnector(config)
        elif db_type == 'postgresql':
            return PostgreSQLConnector(config)
        elif db_type == 'mongodb':
            return MongoDBConnector(config)
        elif db_type == 'redis':
            return RedisConnector(config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

class DatabaseConnection:
    def __init__(self, db_type, host, port, username, password, database,
                 use_ssl=False, connection_timeout=30, retry_attempts=3,
                 pool_size=5, charset='utf8'):
        self.config = {
            'db_type': db_type,
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'database': database,
            'use_ssl': use_ssl,
            'connection_timeout': connection_timeout,
            'retry_attempts': retry_attempts,
            'pool_size': pool_size,
            'charset': charset
        }
        self.connector = DatabaseConnectorFactory.create_connector(self.config)
        self.connection = None

    def connect(self):
        self.connection = self.connector.connect()
        print("Connection successful!")
        return self.connection


if __name__ == "__main__":
    # Example usage
    # Creating different database connections with various configurations
    mysql_db = DatabaseConnection(
        db_type='mysql',
        host='localhost',
        port=3306,
        username='db_user',
        password='password123',
        database='app_db',
        use_ssl=True
    )
    mysql_db.connect()

    mongo_db = DatabaseConnection(
        db_type='mongodb',
        host='mongodb.example.com',
        port=27017,
        username='mongo_user',
        password='mongo123',
        database='analytics',
        pool_size=10,
        retry_attempts=5
    )
    mongo_db.connect()