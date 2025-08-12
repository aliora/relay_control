from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import urllib.parse
import logging

HOST = '0.0.0.0'
PORT = 9748

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # CORS
        self.end_headers()

    def do_OPTIONS(self):
        # CORS preflight response
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self._set_headers()
            resp = {"status": "healthy", "message": "Simple relay server running"}
            self.wfile.write(json.dumps(resp).encode())
        else:
            self._set_headers(404)
            resp = {"status": "error", "message": "Not Found"}
            self.wfile.write(json.dumps(resp).encode())

    def do_POST(self):
        if self.path == '/trigger':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b''

            relay_number = None
            try:
                if 'application/json' in self.headers.get('Content-Type', ''):
                    data = json.loads(post_data.decode())
                    relay_number = data.get('relayNumber')
                else:
                    # Parse query parameters from URL
                    parsed_path = urllib.parse.urlparse(self.path)
                    params = urllib.parse.parse_qs(parsed_path.query)
                    relay_number = params.get('relayNumber', [None])[0]

                logger.info(f"Received relayNumber: {relay_number}")
            except Exception as e:
                logger.warning(f"Parameter parsing error: {e}")

            cmd = ['python3', 'relay_control.py']
            if relay_number:
                cmd.append(str(relay_number))

            logger.info(f"Executing command: {' '.join(cmd)}")

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30,
                    cwd='/home/kubuntu/Projects/USBRelayfinder/relay_control'
                )

                response = {
                    "status": "success",
                    "message": "relay_control.py script executed successfully.",
                    "relayNumber": relay_number,
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip() if result.stderr else None
                }
                self._set_headers(200)
                self.wfile.write(json.dumps(response).encode())

            except subprocess.TimeoutExpired:
                logger.error("Script execution timeout")
                self._set_headers(408)
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": "Script execution timed out."
                }).encode())

            except subprocess.CalledProcessError as e:
                logger.error(f"Script execution error: {e}")
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": f"Script error: {e}",
                    "stderr": e.stderr,
                    "returncode": e.returncode
                }).encode())

            except Exception as e:
                logger.error(f"Server error: {e}")
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": f"Server error: {str(e)}"
                }).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"status": "error", "message": "Not Found"}).encode())

def run():
    logger.info(f"Starting server at http://{HOST}:{PORT}")
    server = HTTPServer((HOST, PORT), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    run()
