"""Automatic Database Migration Manager"""
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import inspect

from app.core.config import settings
from app.core.database import engine

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages automatic database migrations"""
    
    def __init__(self):
        self.alembic_cfg = Config("alembic.ini")
        self.db_path = Path("storage/gamevault.db")
        self.backup_dir = Path("storage/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_database(self) -> Optional[Path]:
        """
        Backup the database before migration
        
        Returns:
            Path to backup file or None if database doesn't exist
        """
        if not self.db_path.exists():
            logger.info("No database file to backup")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"gamevault_{timestamp}.db"
        
        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            raise
    
    def get_current_revision(self) -> Optional[str]:
        """
        Get current database revision
        
        Returns:
            Current revision ID or None if not initialized
        """
        try:
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception as e:
            logger.warning(f"Could not get current revision: {e}")
            return None
    
    def get_head_revision(self) -> str:
        """
        Get the latest available revision from migration scripts
        
        Returns:
            Head revision ID
        """
        script = ScriptDirectory.from_config(self.alembic_cfg)
        return script.get_current_head()
    
    def needs_migration(self) -> bool:
        """
        Check if database needs migration
        
        Returns:
            True if migration is needed, False otherwise
        """
        current = self.get_current_revision()
        head = self.get_head_revision()
        
        if current is None:
            # Database not initialized with Alembic
            return True
        
        return current != head
    
    def database_exists(self) -> bool:
        """Check if database file exists and has tables"""
        if not self.db_path.exists():
            return False
        
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            return len(tables) > 0
        except Exception:
            return False
    
    def run_migration(self, backup: bool = True) -> bool:
        """
        Run database migration automatically
        
        Args:
            backup: Whether to backup database before migration
            
        Returns:
            True if migration was successful, False otherwise
        """
        try:
            # Check if migration is needed
            if not self.needs_migration():
                logger.info("Database is up to date, no migration needed")
                return True
            
            # Backup database if it exists and backup is enabled
            if backup and self.database_exists():
                self.backup_database()
            
            current = self.get_current_revision()
            head = self.get_head_revision()
            
            if current is None:
                logger.info("Initializing database with Alembic...")
                # Stamp the database with current version without running migrations
                command.stamp(self.alembic_cfg, "head")
                logger.info("Database initialized successfully")
            else:
                logger.info(f"Migrating database from {current} to {head}...")
                # Run migration to head
                command.upgrade(self.alembic_cfg, "head")
                logger.info("Database migration completed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Database migration failed: {e}")
            return False
    
    def rollback_migration(self, steps: int = 1) -> bool:
        """
        Rollback migration by specified steps
        
        Args:
            steps: Number of steps to rollback
            
        Returns:
            True if rollback was successful, False otherwise
        """
        try:
            logger.info(f"Rolling back {steps} migration step(s)...")
            command.downgrade(self.alembic_cfg, f"-{steps}")
            logger.info("Rollback completed successfully")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """
        Remove old backup files, keeping only the most recent ones
        
        Args:
            keep_count: Number of recent backups to keep
        """
        try:
            backups = sorted(
                self.backup_dir.glob("gamevault_*.db"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            for backup in backups[keep_count:]:
                backup.unlink()
                logger.info(f"Removed old backup: {backup.name}")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")


# Global migration manager instance
migration_manager = MigrationManager()


def auto_migrate(backup: bool = True) -> bool:
    """
    Automatically run database migration on application startup
    
    This function is designed to be called during application startup.
    It will:
    1. Check if migration is needed
    2. Backup database if requested
    3. Run migration automatically
    4. Cleanup old backups
    
    Args:
        backup: Whether to backup database before migration
        
    Returns:
        True if migration was successful or not needed, False on failure
    """
    try:
        logger.info("Starting automatic database migration check...")
        
        # Run migration
        success = migration_manager.run_migration(backup=backup)
        
        if success and backup:
            # Cleanup old backups
            migration_manager.cleanup_old_backups(keep_count=10)
        
        return success
        
    except Exception as e:
        logger.error(f"Auto-migration failed: {e}")
        return False
