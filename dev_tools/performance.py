import time
import psutil
import requests
from pathlib import Path
from datetime import datetime
import json
import logging

class PerformanceMonitor:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.report_dir = Path("reports/performance")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.report_dir / 'performance.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def measure_page_load(self, path="/"):
        """Measure page load time and resources"""
        url = f"{self.base_url}{path}"
        try:
            start_time = time.time()
            response = requests.get(url)
            load_time = time.time() - start_time
            
            metrics = {
                "url": url,
                "status_code": response.status_code,
                "load_time": f"{load_time:.2f}s",
                "content_size": len(response.content),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Page load metrics for {url}: {metrics}")
            return metrics
        except Exception as e:
            self.logger.error(f"Error measuring page load for {url}: {str(e)}")
            return None

    def monitor_resources(self, duration=60):
        """Monitor system resources during site operation"""
        metrics = []
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                metric = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used": memory.used,
                    "memory_available": memory.available
                }
                metrics.append(metric)
                time.sleep(1)
                
            # Save metrics to file
            report_file = self.report_dir / f"resource_metrics_{int(time.time())}.json"
            with open(report_file, 'w') as f:
                json.dump(metrics, f, indent=2)
                
            self.logger.info(f"Resource monitoring complete. Report saved to {report_file}")
            return metrics
        except Exception as e:
            self.logger.error(f"Error monitoring resources: {str(e)}")
            return None

    def analyze_assets(self):
        """Analyze website assets and their sizes"""
        try:
            response = requests.get(f"{self.base_url}")
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            assets = {
                "scripts": [],
                "styles": [],
                "images": []
            }
            
            # Analyze scripts
            for script in soup.find_all('script', src=True):
                src = script['src']
                size = self._get_asset_size(src)
                assets["scripts"].append({"src": src, "size": size})
            
            # Analyze styles
            for style in soup.find_all('link', rel='stylesheet'):
                href = style['href']
                size = self._get_asset_size(href)
                assets["styles"].append({"href": href, "size": size})
            
            # Analyze images
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    size = self._get_asset_size(src)
                    assets["images"].append({"src": src, "size": size})
            
            # Save analysis
            report_file = self.report_dir / f"asset_analysis_{int(time.time())}.json"
            with open(report_file, 'w') as f:
                json.dump(assets, f, indent=2)
                
            self.logger.info(f"Asset analysis complete. Report saved to {report_file}")
            return assets
        except Exception as e:
            self.logger.error(f"Error analyzing assets: {str(e)}")
            return None

    def _get_asset_size(self, url):
        """Get the size of an asset in bytes"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"{self.base_url}/{url.lstrip('/')}"
            response = requests.head(url)
            return int(response.headers.get('content-length', 0))
        except:
            return 0

    def generate_report(self):
        """Generate a comprehensive performance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "page_loads": {},
            "assets": None,
            "system_resources": None
        }
        
        # Measure main pages
        pages = ['/', '/preferences.html', '/privacy.html', '/terms.html']
        for page in pages:
            metrics = self.measure_page_load(page)
            if metrics:
                report["page_loads"][page] = metrics
        
        # Analyze assets
        report["assets"] = self.analyze_assets()
        
        # Monitor resources for 30 seconds
        report["system_resources"] = self.monitor_resources(30)
        
        # Save report
        report_file = self.report_dir / f"performance_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"Performance report generated: {report_file}")
        return report
