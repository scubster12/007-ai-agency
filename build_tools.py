import os
import shutil
import re
import gzip
import csscompressor
from pathlib import Path
from datetime import datetime

class BuildTools:
    def __init__(self):
        self.src_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.dist_dir = self.src_dir / 'dist'
        self.report_dir = self.src_dir / 'reports'

    def ensure_dir(self, dir_path):
        """Create directory if it doesn't exist"""
        dir_path.mkdir(parents=True, exist_ok=True)

    def minify_js(self, content):
        """Basic JavaScript minification"""
        # Remove comments
        content = re.sub(r'/\*[\s\S]*?\*/', '', content)
        content = re.sub(r'//.*?\n', '\n', content)
        # Remove whitespace
        content = re.sub(r'\s+', ' ', content)
        # Remove whitespace around operators
        content = re.sub(r'\s*([=+\-*/<>!])\s*', r'\1', content)
        return content.strip()

    def minify_css(self, content):
        """Minify CSS using csscompressor"""
        try:
            return csscompressor.compress(content)
        except:
            # Fallback to basic minification if csscompressor fails
            content = re.sub(r'/\*[\s\S]*?\*/', '', content)
            content = re.sub(r'\s+', ' ', content)
            return content.strip()

    def minify_html(self, content):
        """Basic HTML minification"""
        # Remove comments
        content = re.sub(r'<!--[\s\S]*?-->', '', content)
        # Remove whitespace between tags
        content = re.sub(r'>\s+<', '><', content)
        # Remove whitespace at start and end of lines
        content = re.sub(r'^\s+|\s+$', '', content, flags=re.MULTILINE)
        return content.strip()

    def compress_file(self, file_path):
        """Gzip compress a file"""
        with open(file_path, 'rb') as f_in:
            with gzip.open(f'{file_path}.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def copy_assets(self):
        """Copy static assets to dist directory"""
        # Copy images
        src_images = self.src_dir / 'images'
        dist_images = self.dist_dir / 'images'
        if src_images.exists():
            shutil.copytree(src_images, dist_images, dirs_exist_ok=True)

        # Copy other static files (like favicon, robots.txt, etc.)
        static_files = ['favicon.ico', 'robots.txt']
        for file in static_files:
            src_file = self.src_dir / file
            if src_file.exists():
                shutil.copy2(src_file, self.dist_dir)

    def build(self):
        """Build the project for production"""
        print("🚀 Starting build process...")
        build_start = datetime.now()

        # Create dist directory
        self.ensure_dir(self.dist_dir)
        self.ensure_dir(self.report_dir)

        # Process JavaScript files
        js_files = list(self.src_dir.glob('*.js'))
        for js_file in js_files:
            if js_file.name != 'build_tools.py':
                print(f"Processing {js_file.name}...")
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                minified = self.minify_js(content)
                with open(self.dist_dir / js_file.name, 'w', encoding='utf-8') as f:
                    f.write(minified)

        # Process CSS files
        css_files = list(self.src_dir.glob('*.css'))
        for css_file in css_files:
            print(f"Processing {css_file.name}...")
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            minified = self.minify_css(content)
            with open(self.dist_dir / css_file.name, 'w', encoding='utf-8') as f:
                f.write(minified)

        # Process HTML files
        html_files = list(self.src_dir.glob('*.html'))
        for html_file in html_files:
            print(f"Processing {html_file.name}...")
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            minified = self.minify_html(content)
            with open(self.dist_dir / html_file.name, 'w', encoding='utf-8') as f:
                f.write(minified)

        # Copy static assets
        print("Copying assets...")
        self.copy_assets()

        # Compress files
        print("Compressing files...")
        for file in self.dist_dir.glob('**/*.*'):
            if file.is_file() and not file.name.endswith('.gz'):
                self.compress_file(file)

        build_time = datetime.now() - build_start
        print(f"✨ Build completed in {build_time.total_seconds():.2f} seconds!")
        print(f"📦 Production files are in the /dist directory")

        # Generate build report
        report_content = f"""Build Report
=============
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Build Time: {build_time.total_seconds():.2f} seconds

Files Processed:
- JavaScript: {len(js_files)} files
- CSS: {len(css_files)} files
- HTML: {len(html_files)} files

Output Directory: {self.dist_dir}
"""
        with open(self.report_dir / 'build_report.txt', 'w') as f:
            f.write(report_content)

if __name__ == "__main__":
    builder = BuildTools()
    builder.build()
