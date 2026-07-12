import os
import re
import bcrypt
import base64
import hashlib
from cryptography.fernet import Fernet
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from typing import Tuple, Optional


class DataEncryptor:
    """
    Class to encrypt/decrypt recoverable data using Fernet
    """
    
    def __init__(self, key: bytes = None):
        """
        Initialize the encryptor with a key
        
        Args:
            key: Encryption key (if not provided, a new one is generated)
        """
        if key is None:
            self.key = Fernet.generate_key()
        else:
            self.key = key
        self.fernet = Fernet(self.key)
    
    def get_key(self) -> bytes:
        """Return the current key (save this to decrypt later)"""
        return self.key
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt text data
        
        Args:
            data: Text to encrypt
            
        Returns:
            Encrypted text in base64
        """
        if not isinstance(data, str):
            data = str(data)
        
        data_bytes = data.encode('utf-8')
        encrypted_data = self.fernet.encrypt(data_bytes)
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt previously encrypted data
        
        Args:
            encrypted_data: Encrypted text in base64
            
        Returns:
            Decrypted text
            
        Raises:
            cryptography.fernet.InvalidToken: If the key is incorrect
        """
        data_bytes = base64.b64decode(encrypted_data)
        decrypted_data = self.fernet.decrypt(data_bytes)
        return decrypted_data.decode('utf-8')
    
    def encrypt_file(self, file_path: str, output_path: str = None) -> str:
        """
        Encrypt an entire file
        
        Args:
            file_path: Path to the file to encrypt
            output_path: Path to save the encrypted file (optional)
            
        Returns:
            Encrypted data in base64
        """
        with open(file_path, 'rb') as file:
            data = file.read()
        
        encrypted_data = self.fernet.encrypt(data)
        result = base64.b64encode(encrypted_data).decode('utf-8')
        
        if output_path:
            with open(output_path, 'wb') as file:
                file.write(base64.b64decode(result))
        
        return result
    
    def decrypt_file(self, encrypted_data: str, output_path: str):
        """
        Decrypt a file and save it to disk
        
        Args:
            encrypted_data: Encrypted data in base64
            output_path: Path to save the decrypted file
        """
        data_bytes = base64.b64decode(encrypted_data)
        decrypted_data = self.fernet.decrypt(data_bytes)
        
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)

class AESDataEncryptor:
    """
    Alternative using AES to encrypt/decrypt recoverable data
    """
    
    def __init__(self, password: str):
        """
        Initialize the encryptor with a password
        
        Args:
            password: Password to generate the AES key
        """
        self.password = password
        self.key = self._generate_key()
    
    def _generate_key(self) -> bytes:
        """Generate 32-byte AES key from the password"""
        return hashlib.sha256(self.password.encode('utf-8')).digest()
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt data using AES-CBC
        
        Args:
            data: Text to encrypt
            
        Returns:
            Encrypted text in base64 (includes IV)
        """
        # Generate random IV
        iv = os.urandom(16)
        
        # Create cipher
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # Encrypt
        data_bytes = data.encode('utf-8')
        padded_data = pad(data_bytes, AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        
        # Combine IV + encrypted data
        combined = iv + encrypted_data
        return base64.b64encode(combined).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt previously encrypted data with AES
        
        Args:
            encrypted_data: Encrypted text in base64
            
        Returns:
            Decrypted text
        """
        # Decode
        combined = base64.b64decode(encrypted_data)
        
        # Extract IV (first 16 bytes)
        iv = combined[:16]
        encrypted_data_bytes = combined[16:]
        
        # Create cipher
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # Decrypt
        decrypted_data = cipher.decrypt(encrypted_data_bytes)
        
        # Remove padding
        unpadded_data = unpad(decrypted_data, AES.block_size)
        return unpadded_data.decode('utf-8')
    
    def encrypt_with_salt(self, data: str) -> str:
        """
        Encrypt with additional salt for more security
        
        Returns:
            Encrypted text that includes salt + IV + data
        """
        salt = os.urandom(16)
        iv = os.urandom(16)
        
        # Derive key using salt
        key = hashlib.pbkdf2_hmac('sha256', self.password.encode(), salt, 100000)
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data_bytes = data.encode('utf-8')
        padded_data = pad(data_bytes, AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        
        # Combine salt + iv + data
        combined = salt + iv + encrypted_data
        return base64.b64encode(combined).decode('utf-8')
    
    def decrypt_with_salt(self, encrypted_data: str) -> str:
        """
        Decrypt data that was encrypted with salt
        """
        combined = base64.b64decode(encrypted_data)
        
        # Extract salt (16 bytes) + IV (16 bytes)
        salt = combined[:16]
        iv = combined[16:32]
        encrypted_data_bytes = combined[32:]
        
        # Derive key using the same salt
        key = hashlib.pbkdf2_hmac('sha256', self.password.encode(), salt, 100000)
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encrypted_data_bytes)
        unpadded_data = unpad(decrypted_data, AES.block_size)
        
        return unpadded_data.decode('utf-8')

class PasswordHasher:
    """
    Class to hash and verify passwords (irreversible)
    """
    
    def __init__(self, rounds: int = 12):
        """
        Initialize the hasher
        
        Args:
            rounds: Cost factor (higher = more secure but slower)
                   Recommended: 10-12 for production
        """
        self.rounds = rounds
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password irreversibly
        
        Args:
            password: Plain text password
            
        Returns:
            Password hash (to store in database)
        """

        # Convert to bytes and hash
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string to store in database
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify if a password matches its hash
        
        Args:
            password: Plain text password to verify
            hashed: Hash stored in the database
            
        Returns:
            True if the password matches, False otherwise
        """
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        
        try:
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except ValueError:
            # Invalid or malformed hash
            return False
    
    def hash_with_sha256(self, password: str) -> str:
        """
        Hash with SHA-256 first (for very long passwords >72 bytes)
        Useful if you allow extremely long passwords
        """

        # First SHA-256
        sha_hash = hashlib.sha256(password.encode('utf-8')).digest()
        
        # Then bcrypt on the SHA-256 hash
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(sha_hash, salt)
        
        return hashed.decode('utf-8')
    
    def verify_with_sha256(self, password: str, hashed: str) -> bool:
        """Verify password that was hashed with SHA-256 first"""
        
        sha_hash = hashlib.sha256(password.encode('utf-8')).digest()
        hashed_bytes = hashed.encode('utf-8')
        
        try:
            return bcrypt.checkpw(sha_hash, hashed_bytes)
        except ValueError:
            return False
    
    def is_strong_password(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Returns:
            (is_strong, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must have at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must have at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must have at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must have at least one special character"
        
        return True, "Strong password"