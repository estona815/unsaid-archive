"""Loopback-only demonstration server. No archive uploads, storage or external API."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from archive import Archive

BASE = Path(__file__).resolve().parent


def handler(archive, port):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Do not persist questions in request logs.

        def respond(self, code, body, content_type='application/json; charset=utf-8'):
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def valid_host(self):
            return self.headers.get('Host') == '127.0.0.1:%s' % port

        def do_GET(self):
            if not self.valid_host():
                return self.respond(403, b'{}')
            files = {'/': ('index.html','text/html; charset=utf-8'),
                     '/style.css': ('style.css','text/css; charset=utf-8'),
                     '/app.js': ('app.js','text/javascript; charset=utf-8'),
                     '/letters': ('fictional-letters.json','application/json; charset=utf-8')}
            if self.path not in files:
                return self.respond(404,b'{}')
            name, mime = files[self.path]
            return self.respond(200,(BASE/name).read_bytes(),mime)

        def do_POST(self):
            if not self.valid_host() or self.headers.get('Origin') != 'http://127.0.0.1:%s' % port:
                return self.respond(403,b'{}')
            if self.path != '/search':
                return self.respond(404,b'{}')
            try:
                length = int(self.headers.get('Content-Length','0'))
                if not 0 < length <= 8192:
                    raise ValueError('Request too large or empty')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data,dict) or set(data) != {'query'}:
                    raise ValueError('Only a query is accepted')
                query = data['query']
                if not isinstance(query,str) or len(query) > 1200:
                    raise ValueError('Question must contain at most 1200 characters')
                result = archive.search(query)
                self.respond(200,json.dumps(result).encode())
            except (ValueError, TypeError) as error:
                self.respond(400,json.dumps({'error':str(error)}).encode())
    return Handler


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',required=True);p.add_argument('--port',type=int,default=8798)
    args=p.parse_args()
    archive=Archive(json.loads((BASE/'fictional-letters.json').read_text()),args.cache)
    print('Ready at http://127.0.0.1:%s — fictional letters only' % args.port,flush=True)
    HTTPServer(('127.0.0.1',args.port),handler(archive,args.port)).serve_forever()
