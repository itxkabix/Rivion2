import logging
from sqlalchemy import create_engine, inspect
from app.config import settings
from app.services.database import Base

logger = logging.getLogger(__name__)

def init_db():
    """Initialize database - create tables if they don't exist"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        # Check if tables exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            logger.info("📊 Creating database tables...")
            Base.metadata.create_all(engine)
            logger.info("✅ Database tables created successfully!")
            logger.info(f"   Tables: session_user, emotion_log, session_aggregated_emotion")
        else:
            logger.info(f"✅ Database already initialized with {len(existing_tables)} tables")
            logger.info(f"   Tables: {', '.join(existing_tables)}")
            
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise

def get_db_status():
    """Get database connection status"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        return {
            "status": "✅ connected",
            "tables": tables,
            "count": len(tables)
        }
    except Exception as e:
        return {
            "status": "❌ disconnected",
            "error": str(e)
        }

def verify_tables():
    """Verify all required tables exist"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        required_tables = {'session_user', 'emotion_log', 'session_aggregated_emotion'}
        
        missing_tables = required_tables - existing_tables
        if missing_tables:
            logger.warning(f"⚠️ Missing tables: {missing_tables}")
            return False
        
        logger.info(f"✅ All required tables exist")
        return True
    except Exception as e:
        logger.error(f"Error verifying tables: {e}")
        return False
