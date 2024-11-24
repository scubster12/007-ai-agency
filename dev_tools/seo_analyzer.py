import re
import json
import logging
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
from typing import Dict, List, Optional

class SEOAnalyzer:
    def __init__(self):
        self.report_dir = Path("reports/seo")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()
        self.base_url = "https://www.007ai.agency"  # Update with actual base URL

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.report_dir / 'seo.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def analyze_html(self, file_path: Path) -> Dict:
        """Analyze HTML file for SEO optimization"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                soup = BeautifulSoup(content, 'html.parser')
                
            analysis = {
                "file": str(file_path),
                "timestamp": datetime.now().isoformat(),
                "issues": [],
                "recommendations": []
            }
            
            # Check meta tags
            meta_tags = {
                "description": soup.find("meta", {"name": "description"}),
                "keywords": soup.find("meta", {"name": "keywords"}),
                "viewport": soup.find("meta", {"name": "viewport"}),
                "robots": soup.find("meta", {"name": "robots"}),
                "og:title": soup.find("meta", {"property": "og:title"}),
                "og:description": soup.find("meta", {"property": "og:description"}),
                "og:image": soup.find("meta", {"property": "og:image"}),
                "twitter:card": soup.find("meta", {"name": "twitter:card"}),
                "twitter:title": soup.find("meta", {"name": "twitter:title"}),
                "twitter:description": soup.find("meta", {"name": "twitter:description"})
            }
            
            for tag_name, tag in meta_tags.items():
                if not tag:
                    analysis["issues"].append(f"Missing {tag_name} meta tag")
                    analysis["recommendations"].append(f"Add {tag_name} meta tag for better social sharing and SEO")
            
            # Check title
            title = soup.find("title")
            if not title:
                analysis["issues"].append("Missing title tag")
                analysis["recommendations"].append("Add a descriptive title tag")
            elif len(title.text) > 60:
                analysis["issues"].append("Title tag too long (over 60 characters)")
                analysis["recommendations"].append("Shorten title tag to under 60 characters")
            
            # Check headings hierarchy
            headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            h1_count = len(soup.find_all("h1"))
            
            if h1_count == 0:
                analysis["issues"].append("Missing H1 heading")
                analysis["recommendations"].append("Add a single H1 heading as main page title")
            elif h1_count > 1:
                analysis["issues"].append(f"Multiple H1 headings found ({h1_count})")
                analysis["recommendations"].append("Use only one H1 heading per page")
            
            # Check images
            images = soup.find_all("img")
            for img in images:
                if not img.get("alt"):
                    analysis["issues"].append(f"Missing alt text for image: {img.get('src', 'unknown')}")
                    analysis["recommendations"].append("Add descriptive alt text to all images")
            
            # Check links
            links = soup.find_all("a")
            for link in links:
                if not link.get("href"):
                    analysis["issues"].append("Empty link found")
                    analysis["recommendations"].append("Remove empty links or add proper href")
                elif not link.text.strip():
                    analysis["issues"].append("Link without text content")
                    analysis["recommendations"].append("Add descriptive text to all links")
            
            # Check structured data
            structured_data = soup.find_all("script", {"type": "application/ld+json"})
            if not structured_data:
                analysis["issues"].append("No structured data found")
                analysis["recommendations"].append("Add structured data for better search engine understanding")
            
            # Check canonical URL
            canonical = soup.find("link", {"rel": "canonical"})
            if not canonical:
                analysis["issues"].append("Missing canonical URL")
                analysis["recommendations"].append("Add canonical URL to prevent duplicate content issues")
            
            # Check mobile responsiveness meta
            viewport = soup.find("meta", {"name": "viewport"})
            if not viewport:
                analysis["issues"].append("Missing viewport meta tag")
                analysis["recommendations"].append("Add viewport meta tag for mobile responsiveness")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing HTML file {file_path}: {str(e)}")
            return None

    def generate_sitemap(self) -> Optional[str]:
        """Generate XML sitemap"""
        try:
            sitemap_content = []
            sitemap_content.append('<?xml version="1.0" encoding="UTF-8"?>')
            sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
            
            # Scan HTML files in project
            for html_file in Path().rglob("*.html"):
                if "node_modules" not in str(html_file):
                    # Convert file path to URL
                    url_path = str(html_file).replace("\\", "/")
                    if url_path.startswith("index.html"):
                        url = self.base_url + "/"
                    else:
                        url = urljoin(self.base_url + "/", url_path)
                    
                    sitemap_content.append('  <url>')
                    sitemap_content.append(f'    <loc>{url}</loc>')
                    sitemap_content.append('    <changefreq>weekly</changefreq>')
                    sitemap_content.append('    <priority>0.8</priority>')
                    sitemap_content.append('  </url>')
            
            sitemap_content.append('</urlset>')
            
            # Save sitemap
            sitemap_path = Path("public/sitemap.xml")
            sitemap_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(sitemap_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sitemap_content))
            
            self.logger.info(f"Sitemap generated: {sitemap_path}")
            return str(sitemap_path)
            
        except Exception as e:
            self.logger.error(f"Error generating sitemap: {str(e)}")
            return None

    def generate_robots_txt(self) -> Optional[str]:
        """Generate robots.txt file"""
        try:
            robots_content = [
                "User-agent: *",
                "Allow: /",
                "Disallow: /admin/",
                "Disallow: /private/",
                "Disallow: /api/",
                f"Sitemap: {self.base_url}/sitemap.xml"
            ]
            
            # Save robots.txt
            robots_path = Path("public/robots.txt")
            robots_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(robots_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(robots_content))
            
            self.logger.info(f"Robots.txt generated: {robots_path}")
            return str(robots_path)
            
        except Exception as e:
            self.logger.error(f"Error generating robots.txt: {str(e)}")
            return None

    def analyze_performance(self, url: str) -> Dict:
        """Analyze page performance metrics"""
        try:
            analysis = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "metrics": {},
                "recommendations": []
            }
            
            # Simulate basic performance check
            response = requests.get(url)
            
            # Check response time
            response_time = response.elapsed.total_seconds()
            analysis["metrics"]["response_time"] = response_time
            
            if response_time > 2:
                analysis["recommendations"].append("Page load time is too high. Consider optimization.")
            
            # Check content size
            content_size = len(response.content) / 1024  # Size in KB
            analysis["metrics"]["content_size"] = content_size
            
            if content_size > 500:
                analysis["recommendations"].append("Page size is large. Consider compression and optimization.")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance for {url}: {str(e)}")
            return None

    def full_site_analysis(self) -> Dict:
        """Perform full site SEO analysis"""
        try:
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "pages": [],
                "global_issues": [],
                "recommendations": []
            }
            
            # Analyze all HTML files
            html_files = list(Path().rglob("*.html"))
            for html_file in html_files:
                if "node_modules" not in str(html_file):
                    page_analysis = self.analyze_html(html_file)
                    if page_analysis:
                        analysis["pages"].append(page_analysis)
            
            # Generate sitemap
            sitemap_path = self.generate_sitemap()
            if not sitemap_path:
                analysis["global_issues"].append("Failed to generate sitemap")
                analysis["recommendations"].append("Manually create and verify sitemap.xml")
            
            # Generate robots.txt
            robots_path = self.generate_robots_txt()
            if not robots_path:
                analysis["global_issues"].append("Failed to generate robots.txt")
                analysis["recommendations"].append("Manually create and verify robots.txt")
            
            # Save full analysis report
            report_file = self.report_dir / f"full_seo_analysis_{int(datetime.now().timestamp())}.json"
            with open(report_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            self.logger.info(f"Full SEO analysis report generated: {report_file}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error performing full site analysis: {str(e)}")
            return None
