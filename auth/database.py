import asyncpg
from typing import Optional
import uuid
from auth.security import get_password_hash, verify_password
from auth.models import UserCreate, User

class UserDatabase:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = None

    async def initialize(self):
        """Initialize database connection pool and create tables"""
        self.pool = await asyncpg.create_pool(self.db_url)

        # Create users table if it doesn't exist
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Add full_name column if it doesn't exist (migration)
            try:
                await conn.execute('''
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name TEXT
                ''')
            except:
                pass  # Column might already exist in some databases

    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()

    async def create_user(self, user: UserCreate) -> User:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user.password)

        async with self.pool.acquire() as conn:
            await conn.execute(
                '''
                INSERT INTO users (id, username, full_name, email, hashed_password)
                VALUES ($1, $2, $3, $4, $5)
                ''',
                user_id, user.username, user.full_name, user.email, hashed_password
            )

        return User(id=user_id, username=user.username, full_name=user.full_name, email=user.email)

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT id, username, full_name, email, hashed_password FROM users WHERE username = $1',
                username
            )

            if row:
                return {
                    'id': row['id'],
                    'username': row['username'],
                    'full_name': row['full_name'],
                    'email': row['email'],
                    'hashed_password': row['hashed_password']
                }
        return None

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        user = await self.get_user_by_username(username)

        if not user:
            return None

        if not verify_password(password, user['hashed_password']):
            return None

        return User(id=user['id'], username=user['username'], full_name=user['full_name'], email=user['email'])
