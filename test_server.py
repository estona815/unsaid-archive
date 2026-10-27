import http.client
import json
import threading
import unittest
from http.server import HTTPServer
from server import handler

class FakeArchive:
    def search(self, query):
        if not query.strip(): raise ValueError('Text must not be blank')
        return {'query':query,'matches':[]}

class LocalBoundary(unittest.TestCase):
    def setUp(self):
        self.server=HTTPServer(('127.0.0.1',0),handler(FakeArchive(),0))
        self.port=self.server.server_port
        self.server.RequestHandlerClass=handler(FakeArchive(),self.port)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
    def request(self,path='/',method='GET',body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=3)
        conn.request(method,path,body=body,headers=headers or {})
        response=conn.getresponse();result=(response.status,response.read());conn.close();return result
    def test_local_page_and_no_arbitrary_file(self):
        self.assertEqual(self.request()[0],200)
        self.assertEqual(self.request('/archive.py')[0],404)
    def test_foreign_host_denied(self):
        self.assertEqual(self.request(headers={'Host':'attacker.example'})[0],403)
    def test_cross_origin_search_denied(self):
        self.assertEqual(self.request('/search','POST','{"query":"music"}',{'Origin':'https://attacker.example'})[0],403)
    def test_valid_search_and_bad_input(self):
        headers={'Origin':'http://127.0.0.1:%s'%self.port,'Content-Type':'application/json'}
        self.assertEqual(self.request('/search','POST','{"query":"music"}',headers)[0],200)
        self.assertEqual(self.request('/search','POST','{"query":" "}',headers)[0],400)
        self.assertEqual(self.request('/search','POST','{"query":1}',headers)[0],400)

if __name__=='__main__':unittest.main()
