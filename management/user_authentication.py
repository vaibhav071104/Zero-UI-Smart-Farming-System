import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class UserAuthenticationSystem:
    def __init__(self):
        print("User authentication system initialized")
        
        self.data_dir = "management/data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # User database
        self.users = {}
        self.sessions = {}
        
        # Load existing users
        self._load_users()
        
        # Create default admin if no users exist
        if not self.users:
            self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_data = {
            'username': 'admin',
            'password_hash': self._hash_password('admin123'),
            'role': 'admin',
            'email': 'admin@smartfarm.com',
            'created_date': datetime.now().isoformat(),
            'farms': [],
            'permissions': ['all']
        }
        
        self.users['admin'] = admin_data
        self._save_users()
        print("Default admin user created (username: admin, password: admin123)")
    
    def register_user(self, username: str, password: str, email: str, role: str = 'farmer'):
        """Register a new user"""
        try:
            if username in self.users:
                return {'success': False, 'error': 'Username already exists'}
            
            user_data = {
                'username': username,
                'password_hash': self._hash_password(password),
                'role': role,
                'email': email,
                'created_date': datetime.now().isoformat(),
                'farms': [],
                'permissions': ['read', 'write'] if role == 'farmer' else ['read']
            }
            
            self.users[username] = user_data
            self._save_users()
            
            return {'success': True, 'message': f'User {username} registered successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def authenticate_user(self, username: str, password: str):
        """Authenticate user credentials"""
        try:
            if username not in self.users:
                return {'success': False, 'error': 'User not found'}
            
            user = self.users[username]
            password_hash = self._hash_password(password)
            
            if user['password_hash'] != password_hash:
                return {'success': False, 'error': 'Invalid password'}
            
            # Create session
            session_token = self._create_session(username)
            
            return {
                'success': True,
                'session_token': session_token,
                'user_info': {
                    'username': username,
                    'role': user['role'],
                    'email': user['email'],
                    'farms': user['farms']
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_user(self, username: str):
        """Validate if user exists"""
        return username in self.users
    
    def is_admin(self, username: str):
        """Check if user is admin"""
        return username in self.users and self.users[username]['role'] == 'admin'
    
    def get_user_farms(self, username: str):
        """Get farms associated with user"""
        if username in self.users:
            return self.users[username]['farms']
        return []
    
    def add_farm_to_user(self, username: str, farm_id: str):
        """Add farm to user's farm list"""
        if username in self.users:
            if farm_id not in self.users[username]['farms']:
                self.users[username]['farms'].append(farm_id)
                self._save_users()
                return True
        return False
    
    def _hash_password(self, password: str):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _create_session(self, username: str):
        """Create user session"""
        session_token = hashlib.md5(f"{username}{datetime.now()}".encode()).hexdigest()
        self.sessions[session_token] = {
            'username': username,
            'created': datetime.now(),
            'expires': datetime.now() + timedelta(hours=24)
        }
        return session_token
    
    def validate_session(self, session_token: str):
        """Validate session token"""
        if session_token in self.sessions:
            session = self.sessions[session_token]
            if datetime.now() < session['expires']:
                return session['username']
            else:
                del self.sessions[session_token]
        return None
    
    def _save_users(self):
        """Save users to file"""
        try:
            users_file = f"{self.data_dir}/users.json"
            with open(users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def _load_users(self):
        """Load users from file"""
        try:
            users_file = f"{self.data_dir}/users.json"
            if os.path.exists(users_file):
                with open(users_file, 'r') as f:
                    self.users = json.load(f)
                print(f"Loaded {len(self.users)} users")
        except Exception as e:
            print(f"Error loading users: {e}")
