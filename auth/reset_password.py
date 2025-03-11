
import bcrypt
from models.database import User, get_session
import sys

def hash_password(password):
    """Hash a password for storage"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def reset_user_password(username, new_password):
    """Reset a user's password"""
    session = get_session()
    user = session.query(User).filter_by(username=username).first()
    
    if not user:
        return False, f"User '{username}' not found"
    
    # Hash the new password
    hashed_password = hash_password(new_password)
    
    # Update the user's password
    user.password = hashed_password
    session.commit()
    
    return True, f"Password for user '{username}' has been reset"

def list_users():
    """List all users in the database"""
    session = get_session()
    users = session.query(User).all()
    
    print("\nList of users:")
    print("-" * 50)
    for user in users:
        print(f"Username: {user.username}, Email: {user.email}, Department: {user.department}")
    print("-" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  List users: python reset_password.py list")
        print("  Reset password: python reset_password.py reset <username> <new_password>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "list":
        list_users()
    elif action == "reset" and len(sys.argv) == 4:
        username = sys.argv[2]
        new_password = sys.argv[3]
        success, message = reset_user_password(username, new_password)
        print(message)
    else:
        print("Invalid command. Use 'list' to see users or 'reset <username> <new_password>' to reset a password.")
