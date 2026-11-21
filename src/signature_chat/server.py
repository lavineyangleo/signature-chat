import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse, unquote
from signature_chat.services.studio import valid_id


def handler_for(studio):
    web = Path(__file__).parent / 'web'

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, data, code=200, kind='application/json; charset=utf-8', download=False):
            content = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            if download:
                self.send_header('Content-Disposition', 'attachment; filename="signature-transparent.png"')
            self.end_headers()
            self.wfile.write(content)

        def local_host(self):
            return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

        def do_GET(self):
            if not self.local_host():
                return self.send({'error': '仅支持本机访问。'}, 403)
            try:
                url = urlparse(self.path)
                path = unquote(url.path)
                if path == '/api/health':
                    return self.send({'ready': True, 'configured': studio.provider.configured})
                if path == '/api/turns':
                    session = valid_id(parse_qs(url.query).get('session', [''])[0])
                    return self.send(studio.store.rows(session))
                if path.startswith('/images/'):
                    name = path.removeprefix('/images/')
                    if not name.endswith('.png'):
                        raise ValueError('无效文件名。')
                    key = valid_id(name[:-4])
                    target = studio.store.root / 'images' / (key + '.png')
                    return self.send(target.read_bytes(), kind='image/png', download='download' in parse_qs(url.query))
                target = (web / ('index.html' if path == '/' else path.lstrip('/'))).resolve()
                if not target.is_relative_to(web.resolve()):
                    raise ValueError('文件不可访问。')
                if not target.is_file():
                    return self.send({'error': '请先执行 npm --prefix frontend run build。'}, 404)
                return self.send(target.read_bytes(), kind=mimetypes.guess_type(target)[0] or 'application/octet-stream')
            except (ValueError, OSError):
                self.send({'error': '文件或记录不存在。'}, 404)

        def do_POST(self):
            try:
                if not self.local_host():
                    return self.send({'error': '仅支持本机访问。'}, 403)
                origin = self.headers.get('Origin')
                allowed = {'http://' + self.headers.get('Host', ''), 'http://127.0.0.1:5173', 'http://localhost:5173'}
                if origin and origin not in allowed:
                    return self.send({'error': '不允许跨站写入。'}, 403)
                if self.path != '/api/turns':
                    return self.send({'error': '未知接口。'}, 404)
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 16000 or self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                    raise ValueError('请求应为不超过16KB的JSON。')
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict):
                    raise ValueError('请求格式无效。')
                return self.send(studio.submit(body))
            except (ValueError, TypeError, KeyError) as exc:
                self.send({'error': str(exc)}, 400)
            except Exception:
                self.send({'error': '本地处理异常；请检查运行目录权限。'}, 500)

    return Handler


def serve(studio, port):
    server = ThreadingHTTPServer(('127.0.0.1', port), handler_for(studio))
    print(f'Signature Chat: http://127.0.0.1:{port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
