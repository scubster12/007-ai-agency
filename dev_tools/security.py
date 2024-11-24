import os
import json
import logging
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from base64 import b64encode, b64decode

class SecurityManager:
    def __init__(self):
        self.report_dir = Path("reports/security")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()
        self._initialize_keys()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.report_dir / 'security.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_keys(self):
        """Initialize encryption keys"""
        try:
            keys_dir = Path("security/keys")
            keys_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate symmetric key if not exists
            key_file = keys_dir / "symmetric.key"
            if not key_file.exists():
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
            
            # Generate asymmetric keys if not exist
            private_key_file = keys_dir / "private.pem"
            public_key_file = keys_dir / "public.pem"
            
            if not private_key_file.exists() or not public_key_file.exists():
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                
                public_key = private_key.public_key()
                
                # Save private key
                with open(private_key_file, 'wb') as f:
                    f.write(private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    ))
                
                # Save public key
                with open(public_key_file, 'wb') as f:
                    f.write(public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))
            
            self.logger.info("Encryption keys initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing keys: {str(e)}")

    def encrypt_data(self, data, use_symmetric=True):
        """Encrypt data using either symmetric or asymmetric encryption"""
        try:
            if use_symmetric:
                with open("security/keys/symmetric.key", 'rb') as f:
                    key = f.read()
                fernet = Fernet(key)
                return fernet.encrypt(data.encode())
            else:
                with open("security/keys/public.pem", 'rb') as f:
                    public_key = serialization.load_pem_public_key(f.read())
                return public_key.encrypt(
                    data.encode(),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
        except Exception as e:
            self.logger.error(f"Error encrypting data: {str(e)}")
            return None

    def decrypt_data(self, encrypted_data, use_symmetric=True):
        """Decrypt data using either symmetric or asymmetric encryption"""
        try:
            if use_symmetric:
                with open("security/keys/symmetric.key", 'rb') as f:
                    key = f.read()
                fernet = Fernet(key)
                return fernet.decrypt(encrypted_data).decode()
            else:
                with open("security/keys/private.pem", 'rb') as f:
                    private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
                return private_key.decrypt(
                    encrypted_data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode()
        except Exception as e:
            self.logger.error(f"Error decrypting data: {str(e)}")
            return None

    def generate_token(self, length=32):
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)

    def hash_password(self, password, salt=None):
        """Hash password using PBKDF2"""
        try:
            if salt is None:
                salt = os.urandom(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = b64encode(kdf.derive(password.encode())).decode('utf-8')
            salt_hex = b64encode(salt).decode('utf-8')
            
            return f"{salt_hex}${key}"
            
        except Exception as e:
            self.logger.error(f"Error hashing password: {str(e)}")
            return None

    def verify_password(self, password, hash_string):
        """Verify password against hash"""
        try:
            salt_hex, key = hash_string.split('$')
            salt = b64decode(salt_hex.encode())
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key_check = b64encode(kdf.derive(password.encode())).decode('utf-8')
            return key == key_check
            
        except Exception as e:
            self.logger.error(f"Error verifying password: {str(e)}")
            return False

    def security_audit(self):
        """Perform security audit of the project"""
        try:
            audit = {
                "timestamp": datetime.now().isoformat(),
                "checks": []
            }
            
            # Check encryption keys
            keys_dir = Path("security/keys")
            key_files = ["symmetric.key", "private.pem", "public.pem"]
            missing_keys = [f for f in key_files if not (keys_dir / f).exists()]
            
            audit["checks"].append({
                "name": "encryption_keys",
                "status": "passed" if not missing_keys else "failed",
                "message": "All encryption keys present" if not missing_keys else f"Missing keys: {missing_keys}"
            })
            
            # Check file permissions
            if os.name != 'nt':  # Skip on Windows
                for key_file in keys_dir.glob("*"):
                    if key_file.is_file():
                        stats = key_file.stat()
                        mode = stats.st_mode & 0o777
                        audit["checks"].append({
                            "name": f"permissions_{key_file.name}",
                            "status": "passed" if mode == 0o600 else "warning",
                            "message": f"File permissions: {oct(mode)}"
                        })
            
            # Test encryption/decryption
            test_data = "Test encryption"
            encrypted = self.encrypt_data(test_data)
            decrypted = self.decrypt_data(encrypted)
            
            audit["checks"].append({
                "name": "encryption_test",
                "status": "passed" if decrypted == test_data else "failed",
                "message": "Encryption/decryption working correctly" if decrypted == test_data else "Encryption/decryption failed"
            })
            
            # Save audit report
            report_file = self.report_dir / f"security_audit_{int(datetime.now().timestamp())}.json"
            with open(report_file, 'w') as f:
                json.dump(audit, f, indent=2)
            
            self.logger.info(f"Security audit report generated: {report_file}")
            return audit
            
        except Exception as e:
            self.logger.error(f"Error performing security audit: {str(e)}")
            return None

    def analyze_file_security(self, file_path):
        """Analyze security aspects of a specific file"""
        try:
            analysis = {
                "file": str(file_path),
                "timestamp": datetime.now().isoformat(),
                "checks": []
            }
            
            if not Path(file_path).exists():
                return None
            
            # Calculate file hash
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            analysis["file_hash"] = sha256_hash.hexdigest()
            
            # Check for sensitive patterns
            sensitive_patterns = [
                r"password\s*=",
                r"secret\s*=",
                r"api_key\s*=",
                r"token\s*=",
                r"private_key\s*="
            ]
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for pattern in sensitive_patterns:
                    import re
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        analysis["checks"].append({
                            "type": "warning",
                            "message": f"Found potential sensitive data: {pattern}",
                            "count": len(matches)
                        })
            
            # Check file permissions
            if os.name != 'nt':  # Skip on Windows
                stats = Path(file_path).stat()
                mode = stats.st_mode & 0o777
                analysis["checks"].append({
                    "type": "info",
                    "message": f"File permissions: {oct(mode)}"
                })
            
            # Save analysis report
            report_file = self.report_dir / f"file_security_{Path(file_path).name}_{int(datetime.now().timestamp())}.json"
            with open(report_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            self.logger.info(f"File security analysis report generated: {report_file}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing file security: {str(e)}")
            return None
