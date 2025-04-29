"""
Example integration test using TestContainers
Author: Bruno Santos
"""
import pytest
from sqlalchemy import Column, String, Integer, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from testcontainers.postgres import PostgresContainer
import redis

# This is a demo test to show how TestContainers works with SQLAlchemy


# Create a simple model for testing
DemoBase = declarative_base()

class DemoModel(DemoBase):
    """Demo model for testing"""
    __tablename__ = "demo_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    value = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<DemoModel(id={self.id}, name='{self.name}', value='{self.value}')>"


@pytest.mark.integration
class TestTestContainersExample:
    """Test that demonstrates TestContainers integration"""
    
    def test_postgres_container(self, postgres_container):
        """Test that PostgreSQL container is working"""
        # Get connection details
        port = postgres_container.get_exposed_port(5432)
        host = postgres_container.get_container_host_ip()
        
        # Create a database URL
        db_url = f"postgresql://postgres:postgres@{host}:{port}/yvs_test"
        
        # Create engine and session
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        
        # Create tables
        DemoBase.metadata.create_all(engine)
        
        # Create a session
        session = Session()
        
        try:
            # Insert test data
            demo_item = DemoModel(name="test_item", value="test_value")
            session.add(demo_item)
            session.commit()
            
            # Query the data
            result = session.query(DemoModel).filter_by(name="test_item").first()
            
            # Assert the data was inserted correctly
            assert result is not None
            assert result.name == "test_item"
            assert result.value == "test_value"
            
        finally:
            # Clean up
            session.close()
            
            # Drop tables
            DemoBase.metadata.drop_all(engine)
    
    def test_postgres_container_with_direct_connection(self):
        """Test PostgreSQL with a direct connection (not using fixture)"""
        # Create a PostgreSQL container directly in the test
        with PostgresContainer("postgres:13") as postgres:
            # Get connection details
            db_url = postgres.get_connection_url()
            
            # Create engine
            engine = create_engine(db_url)
            
            # Execute a test query
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                value = result.scalar()
                
                # Assert the connection works
                assert value == 1
    
    def test_redis_container(self, redis_container):
        """Test that Redis container is working"""
        # Get connection details
        port = redis_container.get_exposed_port(6379)
        host = redis_container.get_container_host_ip()
        
        # Connect to Redis
        r = redis.Redis(host=host, port=port, db=0)
        
        # Set a value
        r.set("test_key", "test_value")
        
        # Get the value
        result = r.get("test_key")
        
        # Assert the value was set correctly
        assert result is not None
        assert result.decode("utf-8") == "test_value"
        
        # Clean up
        r.delete("test_key")
