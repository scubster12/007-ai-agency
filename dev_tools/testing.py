import unittest
import json
import logging
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup

class WebsiteTests(unittest.TestCase):
    """Test suite for the 007 AI Agency website"""
    
    def setUp(self):
        self.base_url = "http://localhost:8000"
        self.pages = ['/', '/preferences.html', '/privacy.html', '/terms.html']

    def test_pages_load(self):
        """Test that all pages load successfully"""
        for page in self.pages:
            with self.subTest(page=page):
                response = requests.get(f"{self.base_url}{page}")
                self.assertEqual(response.status_code, 200)

    def test_html_validity(self):
        """Test HTML structure and required elements"""
        for page in self.pages:
            with self.subTest(page=page):
                response = requests.get(f"{self.base_url}{page}")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check for required meta tags
                self.assertIsNotNone(soup.find('meta', {'charset': True}))
                self.assertIsNotNone(soup.find('meta', {'name': 'viewport'}))
                
                # Check for title
                self.assertIsNotNone(soup.title)
                
                # Check for main navigation
                self.assertIsNotNone(soup.find('nav'))

    def test_css_loading(self):
        """Test that CSS files are loading"""
        response = requests.get(f"{self.base_url}")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        css_links = soup.find_all('link', rel='stylesheet')
        self.assertGreater(len(css_links), 0)
        
        for css in css_links:
            css_url = css['href']
            if not css_url.startswith(('http://', 'https://')):
                css_url = f"{self.base_url}/{css_url.lstrip('/')}"
            response = requests.get(css_url)
            self.assertEqual(response.status_code, 200)

    def test_javascript_loading(self):
        """Test that JavaScript files are loading"""
        response = requests.get(f"{self.base_url}")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        scripts = soup.find_all('script', src=True)
        self.assertGreater(len(scripts), 0)
        
        for script in scripts:
            script_url = script['src']
            if not script_url.startswith(('http://', 'https://')):
                script_url = f"{self.base_url}/{script_url.lstrip('/')}"
            response = requests.get(script_url)
            self.assertEqual(response.status_code, 200)

    def test_preferences_functionality(self):
        """Test preferences page functionality"""
        response = requests.get(f"{self.base_url}/preferences.html")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for essential elements
        self.assertIsNotNone(soup.find('input', {'id': 'essentialCookies'}))
        self.assertIsNotNone(soup.find('input', {'id': 'analyticsCookies'}))
        self.assertIsNotNone(soup.find('input', {'id': 'marketingCookies'}))

class TestRunner:
    def __init__(self):
        self.report_dir = Path("reports/tests")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.report_dir / 'test.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def run_tests(self):
        """Run all tests and generate report"""
        try:
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromTestCase(WebsiteTests)
            
            # Run tests and capture results
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            # Generate report
            report = {
                "timestamp": datetime.now().isoformat(),
                "tests_run": result.testsRun,
                "tests_passed": result.testsRun - len(result.failures) - len(result.errors),
                "failures": len(result.failures),
                "errors": len(result.errors),
                "details": {
                    "failures": [
                        {
                            "test": str(failure[0]),
                            "message": str(failure[1])
                        }
                        for failure in result.failures
                    ],
                    "errors": [
                        {
                            "test": str(error[0]),
                            "message": str(error[1])
                        }
                        for error in result.errors
                    ]
                }
            }
            
            # Save report
            report_file = self.report_dir / f"test_report_{int(datetime.now().timestamp())}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            self.logger.info(f"Test report generated: {report_file}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error running tests: {str(e)}")
            return None
