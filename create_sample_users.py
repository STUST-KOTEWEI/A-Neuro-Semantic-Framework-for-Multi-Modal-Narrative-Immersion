"""
Create sample users for demonstration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.user_auth import UserManager, UserRegistration, SubscriptionTier, UserRole

def create_sample_users():
    """Create sample users for testing"""
    user_manager = UserManager()
    
    # Sample users
    sample_users = [
        {
            "email": "admin@aireader.com",
            "username": "admin",
            "password": "admin123",
            "subscription_tier": SubscriptionTier.PRO,
            "role": UserRole.ADMIN
        },
        {
            "email": "student@university.edu",
            "username": "student_demo",
            "password": "student123",
            "subscription_tier": SubscriptionTier.EDU,
            "role": UserRole.STUDENT,
            "school_email": "student@university.edu"
        },
        {
            "email": "plus_user@example.com",
            "username": "plus_user",
            "password": "plus123",
            "subscription_tier": SubscriptionTier.PLUS,
            "role": UserRole.USER
        },
        {
            "email": "free_user@example.com",
            "username": "free_user",
            "password": "free123",
            "subscription_tier": SubscriptionTier.FREE,
            "role": UserRole.USER
        }
    ]
    
    for user_data in sample_users:
        # Create registration with proper typing
        reg_data = user_data.copy()
        if 'school_email' in reg_data:
            school_email = reg_data.pop('school_email')
        else:
            school_email = None
            
        registration = UserRegistration(
            email=reg_data['email'],
            username=reg_data['username'],
            password=reg_data['password'],
            subscription_tier=reg_data['subscription_tier'],
            role=reg_data['role'],
            school_email=school_email
        )
        result = user_manager.register_user(registration)
        
        if result["success"]:
            print(f"✅ Created user: {user_data['username']} ({user_data['subscription_tier'].value})")
        else:
            print(f"❌ Failed to create user {user_data['username']}: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    create_sample_users()
    print("\n🎉 Sample users created successfully!")
    print("\nLogin credentials:")
    print("Admin (Pro): admin@aireader.com / admin123")
    print("Student (EDU): student@university.edu / student123") 
    print("Plus User: plus_user@example.com / plus123")
    print("Free User: free_user@example.com / free123")