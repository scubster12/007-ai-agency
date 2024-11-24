import re
import json
import logging
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

class CodeLinter:
    def __init__(self):
        self.report_dir = Path("reports/linting")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.report_dir / 'linting.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def lint_javascript(self, content):
        """Basic JavaScript linting"""
        issues = []
        
        # Check for console.log statements
        console_logs = re.findall(r'console\.log\(', content)
        if console_logs:
            issues.append({
                "type": "warning",
                "message": f"Found {len(console_logs)} console.log statements"
            })
        
        # Check for var usage
        var_usage = re.findall(r'\bvar\b', content)
        if var_usage:
            issues.append({
                "type": "warning",
                "message": "Use 'let' or 'const' instead of 'var'"
            })
        
        # Check for semicolon consistency
        missing_semicolons = re.findall(r'}\n(?![\s}]*(?:else|catch|finally))', content)
        if missing_semicolons:
            issues.append({
                "type": "error",
                "message": "Missing semicolons detected"
            })
        
        return issues

    def lint_css(self, content):
        """Basic CSS linting"""
        issues = []
        
        # Check for !important usage
        important_usage = re.findall(r'!important', content)
        if important_usage:
            issues.append({
                "type": "warning",
                "message": f"Found {len(important_usage)} !important declarations"
            })
        
        # Check for browser-specific prefixes
        prefixes = re.findall(r'(-webkit-|-moz-|-ms-|-o-)', content)
        if prefixes:
            issues.append({
                "type": "info",
                "message": f"Found {len(prefixes)} browser-specific prefixes"
            })
        
        # Check for potential units issues
        zero_units = re.findall(r'0px', content)
        if zero_units:
            issues.append({
                "type": "warning",
                "message": "Use '0' instead of '0px'"
            })
        
        return issues

    def lint_html(self, content):
        """Basic HTML linting"""
        issues = []
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check for missing alt attributes on images
        images = soup.find_all('img')
        missing_alt = [img for img in images if not img.get('alt')]
        if missing_alt:
            issues.append({
                "type": "error",
                "message": f"Found {len(missing_alt)} images missing alt attributes"
            })
        
        # Check for deprecated tags
        deprecated_tags = ['center', 'font', 'strike']
        found_deprecated = []
        for tag in deprecated_tags:
            if soup.find(tag):
                found_deprecated.append(tag)
        if found_deprecated:
            issues.append({
                "type": "error",
                "message": f"Found deprecated HTML tags: {', '.join(found_deprecated)}"
            })
        
        # Check for proper heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings and headings[0].name != 'h1':
            issues.append({
                "type": "warning",
                "message": "First heading is not h1"
            })
        
        return issues

    def lint_file(self, file_path):
        """Lint a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_type = file_path.suffix.lower()
            if file_type == '.js':
                issues = self.lint_javascript(content)
            elif file_type == '.css':
                issues = self.lint_css(content)
            elif file_type == '.html':
                issues = self.lint_html(content)
            else:
                return None
            
            return {
                "file": str(file_path),
                "issues": issues
            }
        except Exception as e:
            self.logger.error(f"Error linting {file_path}: {str(e)}")
            return None

    def lint_project(self):
        """Lint all project files"""
        try:
            project_dir = Path.cwd()
            report = {
                "timestamp": datetime.now().isoformat(),
                "results": []
            }
            
            # Lint JavaScript files
            for js_file in project_dir.glob('**/*.js'):
                if 'node_modules' not in str(js_file):
                    result = self.lint_file(js_file)
                    if result:
                        report["results"].append(result)
            
            # Lint CSS files
            for css_file in project_dir.glob('**/*.css'):
                result = self.lint_file(css_file)
                if result:
                    report["results"].append(result)
            
            # Lint HTML files
            for html_file in project_dir.glob('**/*.html'):
                result = self.lint_file(html_file)
                if result:
                    report["results"].append(result)
            
            # Calculate summary
            report["summary"] = {
                "total_files": len(report["results"]),
                "total_issues": sum(len(r["issues"]) for r in report["results"]),
                "issues_by_type": {
                    "error": sum(1 for r in report["results"] for i in r["issues"] if i["type"] == "error"),
                    "warning": sum(1 for r in report["results"] for i in r["issues"] if i["type"] == "warning"),
                    "info": sum(1 for r in report["results"] for i in r["issues"] if i["type"] == "info")
                }
            }
            
            # Save report
            report_file = self.report_dir / f"lint_report_{int(datetime.now().timestamp())}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            self.logger.info(f"Lint report generated: {report_file}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error linting project: {str(e)}")
            return None
