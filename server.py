import http.server
import socketserver
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import webbrowser
from threading import Thread

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# HTML injection for auto-reload
RELOAD_SCRIPT = """
    <script>
        let socket = new WebSocket('ws://' + window.location.host + '/ws');
        socket.onmessage = function(event) {
            if (event.data === 'reload') window.location.reload();
        };
        socket.onclose = function() {
            console.log('WebSocket closed, attempting to reconnect...');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        };
    </script>
</body>
"""

class AutoReloadHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        super().do_GET()
        if self.path.endswith('.html'):
            content = self.wfile.getvalue().decode('utf-8')
            modified_content = content.replace('</body>', RELOAD_SCRIPT)
            self.wfile = type(self.wfile)(modified_content.encode('utf-8'))

def start_server():
    with socketserver.TCPServer(("", PORT), AutoReloadHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and (
            event.src_path.endswith(('.html', '.css', '.js', '.svg'))
        ):
            print(f"File changed: {event.src_path}")
            # In a real WebSocket implementation, we would send a message to all clients
            # For now, we'll just print the change

def watch_files():
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, DIRECTORY, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Install required package if not present
    try:
        import watchdog
    except ImportError:
        print("Installing required package: watchdog")
        os.system(f"{sys.executable} -m pip install watchdog")
        import watchdog

    # Start server in a separate thread
    server_thread = Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    # Open the browser
    webbrowser.open(f'http://localhost:{PORT}')

    # Start file watcher
    watch_files()
