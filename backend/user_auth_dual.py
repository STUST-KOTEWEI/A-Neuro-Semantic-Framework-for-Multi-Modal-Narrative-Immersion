"""
Enhanced User Authentication with Dual SQL/JSON Backend Support
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
    school_email: Optional[EmailStr] = None


class UserLogin(BaseModel):
    """Enhanced login supporting both email and username"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str
    
    @property
    def identifier(self) -> str:
        """Return the login identifier (email or username)"""
        return self.email or self.username or ""
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.email and not self.username:
            raise ValueError("Either email or username must be provided")


class DualBackendUserManager:
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
            self.use_sql = SQL_AVAILABLE and os.getenv("USE_SQL", "0") == "1"  # Default to JSON for stability
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
                "features": ["premium_tts", "advanced_haptics", "full_analysis", "emotion_detection", "image_generation"]
            },
            SubscriptionTier.PRO: {
                "api_calls_per_day": -1,  # Unlimited
                "max_text_length": -1,   # Unlimited
                "tts_minutes_per_day": -1,  # Unlimited
                "image_generations_per_day": -1,  # Unlimited
                "features": ["all_features", "api_access", "custom_models", "priority_support", "analytics"]
            }
        }
    
    # Common utility methods
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
    
    # Public API methods with backend routing
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
    
    # JSON Backend Implementation
    def _register_user_json(self, registration: UserRegistration) -> Dict[str, Any]:
        """Register user in JSON database"""
        # Check if user already exists
        for user in self.users_db:
            if user["email"] == registration.email or user["username"] == registration.username:
                raise Exception("User with this email or username already exists")
        
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
            "message": "用戶註冊成功",
            "user": {
                "id": user_id,
                "email": registration.email,
                "username": registration.username,
                "subscription_tier": registration.subscription_tier.value,
                "backend": "json"
            },
            "token": token
        }
    
    def _login_user_json(self, login: UserLogin) -> Dict[str, Any]:
        """Login user from JSON database"""
        user = None
        
        # Find user by email or username
        for u in self.users_db:
            if (login.email and u["email"] == login.email) or \
               (login.username and u["username"] == login.username):
                user = u
                break
        
        if not user:
            raise Exception("Invalid credentials")
        
        if not self._verify_password(login.password, user["password_hash"]):
            raise Exception("Invalid credentials")
        
        if not user["is_active"]:
            raise Exception("Account is disabled")
        
        # Update last login
        user["last_login"] = datetime.now().isoformat()
        self._save_users_db()
        
        # Generate token
        token = self._generate_jwt_token(user["id"], user["email"])
        
        return {
            "success": True,
            "message": "登入成功",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "subscription_tier": user["subscription_tier"],
                "backend": "json"
            },
            "token": token
        }
    
    def _get_user_by_id_json(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from JSON database"""
        for user in self.users_db:
            if user["id"] == user_id:
                return {
                    "id": user["id"],
                    "email": user["email"],
                    "username": user["username"],
                    "subscription_tier": user["subscription_tier"],
                    "role": user["role"],
                    "created_at": user["created_at"],
                    "last_login": user["last_login"],
                    "is_active": user["is_active"],
                    "backend": "json"
                }
        return None
    
    # SQL Backend Implementation (simplified for compatibility)
    def _register_user_sql(self, registration: UserRegistration) -> Dict[str, Any]:
        """Register user in SQL database"""
        if not SQL_AVAILABLE:
            raise Exception("SQL backend not available")
        
        # For now, fallback to JSON until SQL schema is properly defined
        print("⚠️ SQL registration not fully implemented, using JSON fallback")
        return self._register_user_json(registration)
    
    def _login_user_sql(self, login: UserLogin) -> Dict[str, Any]:
        """Login user from SQL database"""
        if not SQL_AVAILABLE:
            raise Exception("SQL backend not available")
        
        # For now, fallback to JSON until SQL schema is properly defined
        print("⚠️ SQL login not fully implemented, using JSON fallback")
        return self._login_user_json(login)
    
    def _get_user_by_id_sql(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from SQL database"""
        if not SQL_AVAILABLE:
            return None
        
        # For now, fallback to JSON until SQL schema is properly defined
        print("⚠️ SQL get_user not fully implemented, using JSON fallback")
        return self._get_user_by_id_json(user_id)


    def get_subscription_info(self, user_id: str) -> Dict[str, Any]:
        """Get subscription information for user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}
        
        tier = SubscriptionTier(user["subscription_tier"])
        limits = self.subscription_limits.get(tier, {})
        
        return {
            "subscription_tier": user["subscription_tier"],
            "limits": limits,
            "features": limits.get("features", []),
            "backend": user.get("backend", "json")
        }
    
    def check_usage_limits(self, user_id: str, usage_type: str) -> Dict[str, Any]:
        """Check if user has reached usage limits"""
        user = self.get_user_by_id(user_id)
        if not user:
            return {"allowed": False, "reason": "User not found"}
        
        tier = SubscriptionTier(user["subscription_tier"])
        limits = self.subscription_limits.get(tier, {})
        
        # For demo purposes, return unlimited for now
        return {
            "allowed": True,
            "usage_type": usage_type,
            "current_usage": 0,
            "limit": limits.get(f"{usage_type}s_per_day", -1),
            "backend": user.get("backend", "json")
        }
    
    def increment_usage(self, user_id: str, usage_type: str, amount: int) -> bool:
        """Increment usage counter for user"""
        # For demo purposes, just return True
        # In production, this would update the database
        return True


# Create alias for backwards compatibility
UserManager = DualBackendUserManager