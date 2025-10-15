"""
User Authentication and Subscription Management System
Enhanced with SQL database support
"""

import os
import json
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr

# Try to import SQL components, fallback to JSON if not available
try:
    from sqlalchemy.orm import Session
    from backend.database import User as SQLUser, get_db, create_tables
    SQL_AVAILABLE = True
except ImportError:
    SQL_AVAILABLE = False


class SubscriptionTier(Enum):
    FREE = "free"
    EDU = "edu" 
    PLUS = "plus"
    PRO = "pro"


class UserRole(Enum):
    USER = "user"
    STUDENT = "student"
    EDUCATOR = "educator"
    ADMIN = "admin"


class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    subscription_tier: SubscriptionTier
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    profile: Dict[str, Any] = {}


class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    role: UserRole = UserRole.USER
    school_email: Optional[EmailStr] = None  # For EDU verification


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str
    
    @property
    def identifier(self) -> str:
        return self.email or self.username or ""


class UserManager:
    """
    Enhanced User Manager with dual SQL/JSON support
    Automatically switches between SQL and JSON based on availability
    """
    
    def __init__(self, use_sql: Optional[bool] = None):
        """
        Initialize UserManager with dual backend support
        
        Args:
            use_sql: Force SQL mode (True), JSON mode (False), or auto-detect (None)
        """
        # Auto-detect or use specified backend
        if use_sql is None:
            self.use_sql = SQL_AVAILABLE and os.getenv("USE_SQL", "1") == "1"
        else:
            self.use_sql = use_sql and SQL_AVAILABLE
            
        # Initialize SQL database if available
        if self.use_sql:
            try:
                create_tables()
                print("✅ Using SQL database for user management")
            except Exception as e:
                print(f"⚠️ SQL initialization failed: {e}, falling back to JSON")
                self.use_sql = False
        
        # Initialize JSON fallback
        if not self.use_sql:
            print("📄 Using JSON file for user management")
            
        self.db_path = os.path.join("backend", "db", "users.json")
        self.users_db = self._load_users_db()
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        
        # Determine backend
        if use_sql is None:
            # 暫時停用 SQL backend 以修復前端註冊 500 問題
            self.use_sql = False  # SQL_AVAILABLE
        else:
            self.use_sql = use_sql and SQL_AVAILABLE
            
        if self.use_sql:
            print("Using SQL database for user management")
            create_tables()
        else:
            print("Using JSON file for user management")
            self.users_db = self._load_users_db()
        
        # Subscription limits
        self.subscription_limits = {
            SubscriptionTier.FREE: {
                "api_calls_per_day": 10,
                "max_text_length": 500,
                "tts_minutes_per_day": 5,
                "image_generations_per_day": 3,
                "features": ["basic_tts", "simple_haptics", "text_analysis"]
            },
            SubscriptionTier.EDU: {
                "api_calls_per_day": 100,
                "max_text_length": 2000,
                "tts_minutes_per_day": 30,
                "image_generations_per_day": 20,
                "features": ["advanced_tts", "haptics", "text_analysis", "emotion_detection", "educational_content"]
            },
            SubscriptionTier.PLUS: {
                "api_calls_per_day": 500,
                "max_text_length": 5000,
                "tts_minutes_per_day": 120,
                "image_generations_per_day": 50,
                "features": ["premium_tts", "advanced_haptics", "full_analysis", "emotion_detection", "image_generation", "radio_shows"]
            },
            SubscriptionTier.PRO: {
                "api_calls_per_day": -1,  # Unlimited
                "max_text_length": -1,   # Unlimited
                "tts_minutes_per_day": -1,  # Unlimited
                "image_generations_per_day": -1,  # Unlimited
                "features": ["all_features", "api_access", "custom_models", "priority_support", "analytics"]
            }
        }
    
    def _load_users_db(self) -> List[Dict[str, Any]]:
        """Load users database from JSON file"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            print(f"Error loading users database: {e}")
            return []
    
    def _save_users_db(self) -> None:
        """Save users database to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.users_db, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving users database: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _generate_jwt_token(self, user_id: str, email: str) -> str:
        """Generate JWT token for user session"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register_user(self, registration: UserRegistration) -> Dict[str, Any]:
        """Register new user with dual backend support"""
        if self.use_sql:
            return self._register_user_sql(registration)
        else:
            return self._register_user_json(registration)
    
    def login_user(self, login: UserLogin) -> Dict[str, Any]:
        """Login user with dual backend support"""
        if self.use_sql:
            return self._login_user_sql(login)
        else:
            return self._login_user_json(login)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID with dual backend support"""
        if self.use_sql:
            return self._get_user_by_id_sql(user_id)
        else:
            return self._get_user_by_id_json(user_id)
    
    # SQL Backend Methods
    def _register_user_sql(self, registration: UserRegistration) -> Dict[str, Any]:
        """Register user in SQL database"""
        if not self.use_sql:
            raise Exception("SQL backend not available")
            
        db = next(get_db())
        try:
            # Check if user exists
            existing_user = db.query(SQLUser).filter(
                (SQLUser.email == registration.email) | 
                (SQLUser.username == registration.username)
            ).first()
            
            if existing_user:
                raise Exception("User already exists")
            
            # Create new user
            user_id = self._generate_user_id()
            hashed_password = self._hash_password(registration.password)
            
            sql_user = SQLUser(
                id=user_id,
                email=registration.email,
                username=registration.username,
                password_hash=hashed_password,
                subscription_tier=registration.subscription_tier.value,
                role="user",
                created_at=datetime.utcnow(),
                is_active=True
            )
            
            db.add(sql_user)
            db.commit()
            db.refresh(sql_user)
            
            # Generate token
            token = self._generate_jwt_token(user_id, registration.email)
            
            return {
                "success": True,
                "message": "用戶註冊成功",
                "user": {
                    "id": user_id,
                    "email": registration.email,
                    "username": registration.username,
                    "subscription_tier": registration.subscription_tier.value,
                    "backend": "sql"
                },
                "token": token
            }
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def _login_user_sql(self, login: UserLogin) -> Dict[str, Any]:
        """Login user from SQL database"""
        if not self.use_sql:
            raise Exception("SQL backend not available")
            
        db = next(get_db())
        try:
            # Find user by email or username
            user = None
            if login.email:
                user = db.query(SQLUser).filter(SQLUser.email == login.email).first()
            elif login.username:
                user = db.query(SQLUser).filter(SQLUser.username == login.username).first()
            
            if not user or not self._verify_password(login.password, user.password_hash):
                raise Exception("Invalid credentials")
            
            if not user.is_active:
                raise Exception("Account is disabled")
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Generate token
            token = self._generate_jwt_token(user.id, user.email)
            
            return {
                "success": True,
                "message": "登入成功",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "subscription_tier": user.subscription_tier,
                    "backend": "sql"
                },
                "token": token
            }
            
        finally:
            db.close()
    
    def _get_user_by_id_sql(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from SQL database"""
        if not self.use_sql:
            return None
            
        db = next(get_db())
        try:
            user = db.query(SQLUser).filter(SQLUser.id == user_id).first()
            if user:
                return {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "subscription_tier": user.subscription_tier,
                    "role": user.role,
                    "created_at": user.created_at,
                    "last_login": user.last_login,
                    "is_active": user.is_active,
                    "backend": "sql"
                }
            return None
        finally:
            db.close()
    
    # JSON Backend Methods (existing methods)
    def _register_user_json(self, registration: UserRegistration) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            registration: User registration data
            
        Returns:
            Registration result with user info or error
        """
        # Check if email already exists
        if any(user['email'] == registration.email for user in self.users_db):
            return {"success": False, "error": "Email already registered"}
        
        # Check if username already exists
        if any(user['username'] == registration.username for user in self.users_db):
            return {"success": False, "error": "Username already taken"}
        
        # Validate EDU subscription
        if registration.subscription_tier == SubscriptionTier.EDU:
            if not registration.school_email or not registration.school_email.endswith('.edu'):
                return {"success": False, "error": "Valid .edu email required for EDU subscription"}
        
        # Create new user
        user_id = self._generate_user_id()
        hashed_password = self._hash_password(registration.password)
        
        new_user = {
            "id": user_id,
            "email": registration.email,
            "username": registration.username,
            "password_hash": hashed_password,
            "subscription_tier": registration.subscription_tier.value,
            "role": registration.role.value,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True,
            "profile": {
                "school_email": registration.school_email if registration.school_email else None,
                "api_calls_today": 0,
                "last_api_call_date": None,
                "tts_minutes_today": 0,
                "image_generations_today": 0
            }
        }
        
        self.users_db.append(new_user)
        self._save_users_db()
        
        # Generate token
        token = self._generate_jwt_token(user_id, registration.email)
        
        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": registration.email,
                "username": registration.username,
                "subscription_tier": registration.subscription_tier.value,
                "role": registration.role.value
            },
            "token": token,
            "subscription_limits": self.subscription_limits[registration.subscription_tier]
        }
    
    def login_user(self, login: UserLogin) -> Dict[str, Any]:
        """
        Authenticate user login
        
        Args:
            login: User login credentials
            
        Returns:
            Login result with token or error
        """
        # Determine lookup (email preferred)
        user = None
        if login.email:
            user = next((u for u in self.users_db if u['email'] == login.email), None)
        if not user and login.username:
            user = next((u for u in self.users_db if u['username'] == login.username), None)
        
        if not user:
            return {"success": False, "error": "Invalid credentials"}
        
        if not user['is_active']:
            return {"success": False, "error": "Account is deactivated"}
        
        # Verify password
        if not self._verify_password(login.password, user['password_hash']):
            return {"success": False, "error": "Invalid credentials"}
        
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        self._save_users_db()
        
        # Generate token
        token = self._generate_jwt_token(user['id'], user['email'])
        
        return {
            "success": True,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "username": user['username'],
                "subscription_tier": user['subscription_tier'],
                "role": user['role']
            },
            "token": token,
            "subscription_limits": self.subscription_limits[SubscriptionTier(user['subscription_tier'])]
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return next((u for u in self.users_db if u['id'] == user_id), None)
    
    def check_usage_limits(self, user_id: str, action: str) -> Dict[str, Any]:
        """
        Check if user can perform an action based on subscription limits
        
        Args:
            user_id: User ID
            action: Action type (api_call, tts, image_generation)
            
        Returns:
            Usage check result
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return {"allowed": False, "error": "User not found"}
        
        subscription_tier = SubscriptionTier(user['subscription_tier'])
        limits = self.subscription_limits[subscription_tier]
        
        # Reset daily counters if new day
        today = datetime.now().date().isoformat()
        if user['profile'].get('last_api_call_date') != today:
            user['profile']['api_calls_today'] = 0
            user['profile']['tts_minutes_today'] = 0
            user['profile']['image_generations_today'] = 0
            user['profile']['last_api_call_date'] = today
            self._save_users_db()
        
        # Check limits
        if action == "api_call":
            daily_limit = limits["api_calls_per_day"]
            current_usage = user['profile']['api_calls_today']
        elif action == "tts":
            daily_limit = limits["tts_minutes_per_day"]
            current_usage = user['profile']['tts_minutes_today']
        elif action == "image_generation":
            daily_limit = limits["image_generations_per_day"]
            current_usage = user['profile']['image_generations_today']
        else:
            return {"allowed": False, "error": "Unknown action"}
        
        # -1 means unlimited
        if daily_limit == -1:
            return {"allowed": True, "usage": current_usage, "limit": "unlimited"}
        
        if current_usage >= daily_limit:
            return {
                "allowed": False, 
                "error": f"Daily {action} limit exceeded",
                "usage": current_usage,
                "limit": daily_limit
            }
        
        return {
            "allowed": True,
            "usage": current_usage,
            "limit": daily_limit,
            "remaining": daily_limit - current_usage
        }
    
    def increment_usage(self, user_id: str, action: str, amount: int = 1) -> bool:
        """Increment usage counter for user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        if action == "api_call":
            user['profile']['api_calls_today'] += amount
        elif action == "tts":
            user['profile']['tts_minutes_today'] += amount
        elif action == "image_generation":
            user['profile']['image_generations_today'] += amount
        
        self._save_users_db()
        return True
    
    def get_subscription_info(self, user_id: str) -> Dict[str, Any]:
        """Get user's subscription information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}
        
        subscription_tier = SubscriptionTier(user['subscription_tier'])
        limits = self.subscription_limits[subscription_tier]
        
        return {
            "subscription_tier": subscription_tier.value,
            "limits": limits,
            "current_usage": {
                "api_calls_today": user['profile'].get('api_calls_today', 0),
                "tts_minutes_today": user['profile'].get('tts_minutes_today', 0),
                "image_generations_today": user['profile'].get('image_generations_today', 0)
            }
        }


# Example usage and testing
if __name__ == "__main__":
    user_manager = UserManager()
    
    # Test registration
    test_registration = UserRegistration(
        email="test@example.com",
        username="testuser",
        password="password123",
        subscription_tier=SubscriptionTier.PLUS
    )
    
    result = user_manager.register_user(test_registration)
    print("Registration result:", result)
    
    # Test login
    test_login = UserLogin(
        email="test@example.com",
        password="password123"
    )
    
    login_result = user_manager.login_user(test_login)
    print("Login result:", login_result)