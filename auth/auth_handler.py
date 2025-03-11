from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import PasswordReset, User, JobTitle, get_session

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    session = get_session()
    return session.query(User).get(int(user_id))

def create_user(username, email, password, department, job_title):
    session = get_session()

    # Save job title if it doesn't exist
    existing_title = session.query(JobTitle).filter_by(title=job_title).first()
    if not existing_title:
        new_title = JobTitle(title=job_title)
        session.add(new_title)
        session.commit()

    # Use the default method (pbkdf2:sha256) for password hashing
    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        department=department,
        job_title=job_title
    )
    session.add(new_user)
    session.commit()
    return new_user

def authenticate_user(username, password):
    session = get_session()
    user = session.query(User).filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

def get_job_titles():
    session = get_session()
    titles = session.query(JobTitle.title).all()
    return [title[0] for title in titles]

DEPARTMENTS = [
    "Engineering",
    "Finance",
    "Quality Assurance",
    "Warehouse",
    "Sales",
    "Human Resources"
]
import bcrypt
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from models.database import User, JobTitle, TwoFactorAuth, get_session

# Departments list
DEPARTMENTS = [
    "Engineering", 
    "Finance", 
    "Quality Assurance", 
    "Warehouse", 
    "Sales", 
    "Human Resources"
]

def hash_password(password):
    """Hash a password for storage"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    try:
        return bcrypt.checkpw(
            provided_password.encode('utf-8'), 
            stored_password.encode('utf-8')
        )
    except ValueError:
        # For compatibility with passwords that might have been hashed differently
        return False

def create_user(username, email, password, department, job_title, two_factor_enabled=False):
    """Create a new user in the database"""
    session = get_session()
    
    # Check if username already exists
    if session.query(User).filter_by(username=username).first():
        raise ValueError("Username already exists")
    
    # Check if email already exists
    if session.query(User).filter_by(email=email).first():
        raise ValueError("Email already exists")
    
    # Convert boolean to integer for PostgreSQL compatibility
    two_factor_enabled_int = 1 if two_factor_enabled else 0

    # Hash the password
    hashed_password = generate_password_hash(password)
    
    # Create new user
    new_user = User(
        username=username,
        email=email,
        password=hash_password(password),
        department=department,
        job_title=job_title,
        two_factor_enabled=two_factor_enabled
    )
    
    # Add job title if it doesn't exist
    if not session.query(JobTitle).filter_by(title=job_title).first():
        new_job_title = JobTitle(title=job_title)
        session.add(new_job_title)
    
    session.add(new_user)
    session.commit()
    
    return new_user

def authenticate_user(username, password, two_factor_code=None):
    """Authenticate a user by username and password"""
    session = get_session()
    user = session.query(User).filter_by(username=username).first()
    
    if not user:
        return None
    
    if not check_password(user.password, password):
        return None
    
    # Check 2FA if enabled
    if user.two_factor_enabled:
        if not two_factor_code:
            return "2FA_REQUIRED"
        
        tfa = session.query(TwoFactorAuth).filter_by(user_id=user.id).first()
        if not tfa:
            return None
        
        totp = pyotp.TOTP(tfa.secret_key)
        if not totp.verify(two_factor_code):
            return None
    
    return user

def generate_2fa_qrcode(user_id):
    """Generate a 2FA QR code for a user"""
    session = get_session()
    user = session.query(User).get(user_id)
    
    if not user:
        return None, "User not found"
    
    # Create or get existing 2FA record
    tfa = session.query(TwoFactorAuth).filter_by(user_id=user.id).first()
    
    if not tfa:
        # Generate a new secret key
        secret_key = pyotp.random_base32()
        tfa = TwoFactorAuth(user_id=user.id, secret_key=secret_key)
        session.add(tfa)
        session.commit()
    
    # Generate QR code
    totp = pyotp.TOTP(tfa.secret_key)
    uri = totp.provisioning_uri(user.email, issuer_name="Waste Management App")
    
    img = qrcode.make(uri)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str, tfa.secret_key

def verify_2fa_setup(user_id, verification_code):
    """Verify the 2FA setup with a verification code"""
    session = get_session()
    tfa = session.query(TwoFactorAuth).filter_by(user_id=user_id).first()
    
    if not tfa:
        return False, "2FA not set up for this user"
    
    totp = pyotp.TOTP(tfa.secret_key)
    if totp.verify(verification_code):
        # Enable 2FA for the user
        user = session.query(User).get(user_id)
        user.two_factor_enabled = True
        session.commit()
        return True, "2FA successfully enabled"
    
    return False, "Invalid verification code"

def disable_2fa(user_id):
    """Disable 2FA for a user"""
    session = get_session()
    user = session.query(User).get(user_id)
    
    if not user:
        return False, "User not found"
    
    tfa = session.query(TwoFactorAuth).filter_by(user_id=user_id).first()
    if tfa:
        session.delete(tfa)
    
    user.two_factor_enabled = False
    session.commit()
    
    return True, "2FA successfully disabled"

def update_user(user_id, email=None, department=None, job_title=None):
    """Update user information"""
    session = get_session()
    user = session.query(User).get(user_id)
    
    if not user:
        return False, "User not found"
    
    if email and email != user.email:
        # Check if email is already taken
        if session.query(User).filter_by(email=email).first():
            return False, "Email already in use"
        user.email = email
    
    if department:
        user.department = department
    
    if job_title:
        user.job_title = job_title
        # Add job title if it doesn't exist
        if not session.query(JobTitle).filter_by(title=job_title).first():
            new_job_title = JobTitle(title=job_title)
            session.add(new_job_title)
    
    session.commit()
    return True, "User information updated successfully"

def delete_user(username):
    """Delete a user from the database"""
    session = get_session()
    user = session.query(User).filter_by(username=username).first()
    
    if not user:
        raise ValueError(f"User {username} not found")
    
    # Delete user's 2FA record if exists
    tfa = session.query(TwoFactorAuth).filter_by(user_id=user.id).first()
    if tfa:
        session.delete(tfa)
    
    # Delete the user
    session.delete(user)
    session.commit()
    
    return True

def generate_password_reset_token(username):
    """Generate a password reset token for a user"""
    session = get_session()
    user = session.query(User).filter_by(username=username).first()
    
    if not user:
        return None
    
    # Generate a secure token
    token = pyotp.random_base32()
    
    # Store token in database
    reset = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    session.add(reset)
    session.commit()
    
    return token

def verify_password_reset_token(token):
    """Verify a password reset token"""
    session = get_session()
    reset = session.query(PasswordReset).filter_by(token=token).first()
    
    if not reset:
        return None
    
    # Check if token is expired
    if reset.expires_at < datetime.utcnow():
        session.delete(reset)
        session.commit()
        return None
    
    return reset.user_id

def get_job_titles():
    """Get all job titles from the database"""
    session = get_session()
    job_titles = session.query(JobTitle.title).all()
    return [title[0] for title in job_titles]

def get_all_users():
    """Get all users from the database"""
    session = get_session()
    return session.query(User).all()
