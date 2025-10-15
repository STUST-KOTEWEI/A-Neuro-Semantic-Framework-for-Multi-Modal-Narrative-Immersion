"""
Enhanced User Authentication System with SQL Database
"""

import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.database import User, BroadcastSession, APIUsageLog, get_db, create_tables


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


class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    role: UserRole = UserRole.USER
    school_email: Optional[EmailStr] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class DatabaseUserManager:
    """
    Enhanced user manager with SQL database support
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize user manager with database
        
        Args:
            secret_key: JWT secret key
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
        
        # Create tables if they don't exist
        create_tables()
        
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
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _generate_jwt_token(self, user_id: int, email: str) -> str:
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
    
    def register_user(self, registration: UserRegistration, db: Session = None) -> Dict[str, Any]:
        """
        Register a new user in database
        
        Args:
            registration: User registration data
            db: Database session
            
        Returns:
            Registration result with user info or error
        """
        if db is None:
            db = next(get_db())
        
        try:
            # Check if email already exists
            existing_user = db.query(User).filter(User.email == registration.email).first()
            if existing_user:
                return {"success": False, "error": "Email already registered"}
            
            # Check if username already exists
            existing_username = db.query(User).filter(User.username == registration.username).first()
            if existing_username:
                return {"success": False, "error": "Username already taken"}
            
            # Validate EDU subscription
            if registration.subscription_tier == SubscriptionTier.EDU:
                if not registration.school_email or not registration.school_email.endswith('.edu'):
                    return {"success": False, "error": "Valid .edu email required for EDU subscription"}
            
            # Create new user
            hashed_password = self._hash_password(registration.password)
            
            new_user = User(
                email=registration.email,
                username=registration.username,
                password_hash=hashed_password,
                subscription_tier=registration.subscription_tier.value,
                role=registration.role.value,
                school_email=registration.school_email,
                created_at=datetime.utcnow(),
                is_active=True,
                api_calls_today=0,
                tts_minutes_today=0.0,
                image_generations_today=0,
                last_usage_reset=datetime.utcnow()
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Generate token
            token = self._generate_jwt_token(new_user.id, new_user.email)
            
            return {
                "success": True,
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "username": new_user.username,
                    "subscription_tier": new_user.subscription_tier,
                    "role": new_user.role
                },
                "token": token,
                "subscription_limits": self.subscription_limits[registration.subscription_tier]
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"Registration failed: {str(e)}"}
        finally:
            db.close()
    
    def login_user(self, login: UserLogin, db: Session = None) -> Dict[str, Any]:
        """
        Authenticate user login
        
        Args:
            login: User login credentials
            db: Database session
            
        Returns:
            Login result with token or error
        """
        if db is None:
            db = next(get_db())
        
        try:
            # Find user by email
            user = db.query(User).filter(User.email == login.email).first()
            
            if not user:
                return {"success": False, "error": "Invalid email or password"}
            
            if not user.is_active:
                return {"success": False, "error": "Account is deactivated"}
            
            # Verify password
            if not self._verify_password(login.password, user.password_hash):
                return {"success": False, "error": "Invalid email or password"}
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Generate token
            token = self._generate_jwt_token(user.id, user.email)
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "subscription_tier": user.subscription_tier,
                    "role": user.role
                },
                "token": token,
                "subscription_limits": self.subscription_limits[SubscriptionTier(user.subscription_tier)]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Login failed: {str(e)}"}
        finally:
            db.close()
    
    def get_user_by_id(self, user_id: int, db: Session = None) -> Optional[User]:
        """Get user by ID from database"""
        if db is None:
            db = next(get_db())
        
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
    
    def check_usage_limits(self, user_id: int, action: str, db: Session = None) -> Dict[str, Any]:
        """
        Check if user can perform an action based on subscription limits
        
        Args:
            user_id: User ID
            action: Action type (api_call, tts, image_generation)
            db: Database session
            
        Returns:
            Usage check result
        """
        if db is None:
            db = next(get_db())
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"allowed": False, "error": "User not found"}
            
            subscription_tier = SubscriptionTier(user.subscription_tier)
            limits = self.subscription_limits[subscription_tier]
            
            # Reset daily counters if new day
            today = datetime.now().date()
            last_reset = user.last_usage_reset.date() if user.last_usage_reset else today
            
            if last_reset != today:
                user.api_calls_today = 0
                user.tts_minutes_today = 0.0
                user.image_generations_today = 0
                user.last_usage_reset = datetime.utcnow()
                db.commit()
            
            # Check limits
            if action == "api_call":
                daily_limit = limits["api_calls_per_day"]
                current_usage = user.api_calls_today
            elif action == "tts":
                daily_limit = limits["tts_minutes_per_day"]
                current_usage = user.tts_minutes_today
            elif action == "image_generation":
                daily_limit = limits["image_generations_per_day"]
                current_usage = user.image_generations_today
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
            
        except Exception as e:
            return {"allowed": False, "error": f"Usage check failed: {str(e)}"}
        finally:
            db.close()
    
    def increment_usage(self, user_id: int, action: str, amount: float = 1, db: Session = None) -> bool:
        """Increment usage counter for user"""
        if db is None:
            db = next(get_db())
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            if action == "api_call":
                user.api_calls_today += int(amount)
            elif action == "tts":
                user.tts_minutes_today += amount
            elif action == "image_generation":
                user.image_generations_today += int(amount)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Failed to increment usage: {e}")
            return False
        finally:
            db.close()
    
    def get_subscription_info(self, user_id: int, db: Session = None) -> Dict[str, Any]:
        """Get user's subscription information"""
        if db is None:
            db = next(get_db())
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            subscription_tier = SubscriptionTier(user.subscription_tier)
            limits = self.subscription_limits[subscription_tier]
            
            return {
                "subscription_tier": subscription_tier.value,
                "limits": limits,
                "current_usage": {
                    "api_calls_today": user.api_calls_today,
                    "tts_minutes_today": user.tts_minutes_today,
                    "image_generations_today": user.image_generations_today
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get subscription info: {str(e)}"}
        finally:
            db.close()
    
    def log_api_usage(self, user_id: int, endpoint: str, method: str, status: int, processing_time_ms: float = None, db: Session = None):
        """Log API usage for analytics"""
        if db is None:
            db = next(get_db())
        
        try:
            log_entry = APIUsageLog(
                user_id=user_id,
                endpoint=endpoint,
                method=method,
                response_status=status,
                processing_time_ms=processing_time_ms,
                timestamp=datetime.utcnow()
            )
            
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            db.rollback()
            print(f"Failed to log API usage: {e}")
        finally:
            db.close()


# Export for backward compatibility
UserManager = DatabaseUserManager

if __name__ == "__main__":
    # Test the database user manager
    user_manager = DatabaseUserManager()
    
    # Test registration
    test_registration = UserRegistration(
        email="test@example.com",
        username="testuser",
        password="password123",
        subscription_tier=SubscriptionTier.PLUS
    )
    
    result = user_manager.register_user(test_registration)
    print("Registration result:", result)