import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
import subprocess
import zipfile

class Deployer:
    def __init__(self):
        self.report_dir = Path("reports/deployment")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.dist_dir = Path("dist")
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.report_dir / 'deployment.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_deployment_package(self):
        """Create a deployment package with all necessary files"""
        try:
            # Ensure dist directory exists
            if not self.dist_dir.exists():
                self.logger.error("Dist directory not found. Run build process first.")
                return None

            # Create deployment directory
            deploy_dir = Path("deploy")
            deploy_dir.mkdir(exist_ok=True)
            
            # Create version-specific directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version_dir = deploy_dir / f"007ai_agency_{timestamp}"
            version_dir.mkdir(exist_ok=True)
            
            # Copy dist files
            shutil.copytree(self.dist_dir, version_dir / "static", dirs_exist_ok=True)
            
            # Copy server files
            server_files = ["server.py", "requirements.txt"]
            for file in server_files:
                if Path(file).exists():
                    shutil.copy2(file, version_dir)
            
            # Create deployment config
            config = {
                "version": timestamp,
                "deployment_date": datetime.now().isoformat(),
                "files": {
                    "static": [f.name for f in (version_dir / "static").rglob("*") if f.is_file()],
                    "server": [f.name for f in version_dir.glob("*.py")],
                    "config": [f.name for f in version_dir.glob("*.txt")]
                }
            }
            
            with open(version_dir / "deployment_config.json", 'w') as f:
                json.dump(config, f, indent=2)
            
            # Create deployment instructions
            instructions = f"""007 AI Agency Deployment Instructions
===============================
Version: {timestamp}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

1. Server Requirements
   - Python 3.8 or higher
   - Install dependencies: pip install -r requirements.txt

2. Configuration
   - Update server.py with production settings
   - Configure SSL certificates
   - Set environment variables

3. Deployment Steps
   a. Copy all files to production server
   b. Install dependencies
   c. Configure web server (nginx/apache)
   d. Start application server
   e. Verify deployment

4. File Structure
   /static    - Static files (HTML, CSS, JS)
   /server.py - Main server file
   /requirements.txt - Python dependencies

5. Security Notes
   - Update SSL certificates
   - Configure firewall rules
   - Set secure permissions
   - Enable rate limiting

6. Monitoring
   - Check server logs
   - Monitor performance
   - Track error rates
   - Watch resource usage

For support: support@007ai.agency
"""
            
            with open(version_dir / "DEPLOY.txt", 'w') as f:
                f.write(instructions)
            
            # Create ZIP archive
            zip_file = deploy_dir / f"007ai_agency_{timestamp}.zip"
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file in version_dir.rglob("*"):
                    if file.is_file():
                        zf.write(file, file.relative_to(version_dir))
            
            # Generate deployment report
            report = {
                "version": timestamp,
                "timestamp": datetime.now().isoformat(),
                "package_location": str(zip_file),
                "package_size": os.path.getsize(zip_file),
                "files": config["files"],
                "checksum": self._get_file_checksum(zip_file)
            }
            
            report_file = self.report_dir / f"deployment_report_{timestamp}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Deployment package created: {zip_file}")
            self.logger.info(f"Deployment report generated: {report_file}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error creating deployment package: {str(e)}")
            return None

    def _get_file_checksum(self, file_path):
        """Calculate file checksum"""
        try:
            import hashlib
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except:
            return None

    def verify_deployment(self, package_path):
        """Verify deployment package integrity"""
        try:
            if not Path(package_path).exists():
                self.logger.error(f"Package not found: {package_path}")
                return False
            
            verification = {
                "timestamp": datetime.now().isoformat(),
                "package": str(package_path),
                "checks": []
            }
            
            # Check ZIP integrity
            with zipfile.ZipFile(package_path, 'r') as zf:
                bad_files = zf.testzip()
                verification["checks"].append({
                    "name": "zip_integrity",
                    "status": "passed" if bad_files is None else "failed",
                    "message": "All files OK" if bad_files is None else f"Corrupted files found: {bad_files}"
                })
            
            # Extract and verify files
            temp_dir = Path("temp_verify")
            temp_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(package_path, 'r') as zf:
                zf.extractall(temp_dir)
            
            # Check required files
            required_files = ["server.py", "requirements.txt", "deployment_config.json", "DEPLOY.txt"]
            missing_files = [f for f in required_files if not (temp_dir / f).exists()]
            
            verification["checks"].append({
                "name": "required_files",
                "status": "passed" if not missing_files else "failed",
                "message": "All required files present" if not missing_files else f"Missing files: {missing_files}"
            })
            
            # Check static files
            static_dir = temp_dir / "static"
            if not static_dir.exists():
                verification["checks"].append({
                    "name": "static_files",
                    "status": "failed",
                    "message": "Static directory not found"
                })
            else:
                static_files = list(static_dir.rglob("*"))
                verification["checks"].append({
                    "name": "static_files",
                    "status": "passed",
                    "message": f"Found {len(static_files)} static files"
                })
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            # Save verification report
            report_file = self.report_dir / f"verification_report_{int(datetime.now().timestamp())}.json"
            with open(report_file, 'w') as f:
                json.dump(verification, f, indent=2)
            
            self.logger.info(f"Verification report generated: {report_file}")
            return verification
            
        except Exception as e:
            self.logger.error(f"Error verifying deployment: {str(e)}")
            return None
