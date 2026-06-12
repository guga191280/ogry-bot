import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class DecryptHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/decrypt':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                encrypted_text = data.get('text', '')
                
                if not encrypted_text:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'Missing text field')
                    return
                
                # Запускаем бинарник дешифратора с переданным текстом
                result = subprocess.run(
                    ['./linux-x64_x86', encrypted_text], 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                
                # Берем то, что программа вывела в консоль
                decrypted_text = result.stdout.strip()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = json.dumps({'decrypted': decrypted_text})
                self.wfile.write(response.encode('utf-8'))
                
            except subprocess.CalledProcessError as e:
                self.send_response(500)
                self.end_headers()
                error_msg = f"Decryption binary error: {e.stderr.strip()}"
                self.wfile.write(json.dumps({'error': error_msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DecryptHandler)
    print(f"🚀 Дешифратор-сервер запущен на порту {port} внутри WSL...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен.")

if __name__ == '__main__':
    run()
