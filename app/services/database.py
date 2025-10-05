import os
import asyncpg
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn: Optional[asyncpg.Connection] = None
    
    async def connect(self):
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL tidak ditemukan!")
        
        self.conn = await asyncpg.connect(database_url)
        await self.create_tables()
    
    async def create_tables(self):
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                is_premium BOOLEAN DEFAULT FALSE,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_usage (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                action_type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details JSONB
            )
        ''')
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.conn.fetchrow(
            'SELECT * FROM users WHERE user_id = $1', user_id
        )
    
    async def get_all_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.conn.fetch(
            'SELECT * FROM users ORDER BY created_at DESC LIMIT $1', limit
        )
    
    async def create_user(self, user_data: Dict[str, Any]) -> None:
        await self.conn.execute('''
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            updated_at = CURRENT_TIMESTAMP
        ''', user_data['user_id'], user_data['username'], 
           user_data['first_name'], user_data['last_name'])
    
    async def update_user_usage(self, user_id: int, action_type: str) -> None:
        await self.conn.execute('''
            INSERT INTO user_usage (user_id, action_type)
            VALUES ($1, $2)
        ''', user_id, action_type)
        
        await self.conn.execute('''
            UPDATE users 
            SET usage_count = usage_count + 1, 
                updated_at = CURRENT_TIMESTAMP 
            WHERE user_id = $1
        ''', user_id)
    
    async def update_user_premium(self, user_id: int, is_premium: bool) -> None:
        await self.conn.execute('''
            UPDATE users 
            SET is_premium = $1, 
                updated_at = CURRENT_TIMESTAMP 
            WHERE user_id = $2
        ''', is_premium, user_id)
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Mendapatkan statistik penggunaan bot"""
        # Total users
        total_users = await self.conn.fetchval('SELECT COUNT(*) FROM users')
        
        # Premium users
        premium_users = await self.conn.fetchval('SELECT COUNT(*) FROM users WHERE is_premium = true')
        
        # Total usage
        total_usage = await self.conn.fetchval('SELECT COUNT(*) FROM user_usage')
        
        # Active users (30 hari terakhir)
        active_users = await self.conn.fetchval('''
            SELECT COUNT(DISTINCT user_id) FROM user_usage 
            WHERE timestamp >= NOW() - INTERVAL '30 days'
        ''')
        
        # Usage hari ini
        today_usage = await self.conn.fetchval('''
            SELECT COUNT(*) FROM user_usage 
            WHERE DATE(timestamp) = CURRENT_DATE
        ''')
        
        # Usage bulan ini
        month_usage = await self.conn.fetchval('''
            SELECT COUNT(*) FROM user_usage 
            WHERE EXTRACT(MONTH FROM timestamp) = EXTRACT(MONTH FROM CURRENT_DATE)
            AND EXTRACT(YEAR FROM timestamp) = EXTRACT(YEAR FROM CURRENT_DATE)
        ''')
        
        return {
            'total_users': total_users,
            'premium_users': premium_users,
            'total_usage': total_usage,
            'active_users': active_users,
            'today_usage': today_usage,
            'month_usage': month_usage
        }

# Global database instance
db = Database()

async def init_db():
    await db.connect()

async def get_user(user_id: int):
    return await db.get_user(user_id)

async def get_all_users(limit: int = 100):
    return await db.get_all_users(limit)

async def create_user(user_data: Dict[str, Any]):
    return await db.create_user(user_data)

async def update_user_usage(user_id: int, action_type: str):
    return await db.update_user_usage(user_id, action_type)

async def update_user_premium(user_id: int, is_premium: bool):
    return await db.update_user_premium(user_id, is_premium)

async def get_usage_stats():
    return await db.get_usage_stats()