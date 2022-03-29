import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import json



class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html("hi!"))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        content_len = int(self.headers.get('Content-Length'))
        json_data = json.loads(self.rfile.read(content_len))

        probability = self.get_infection_probability(json_data)

        ### CHAMAR O MODELO
        self.wfile.write(str(probability*100).encode("utf8"))

    def get_infection_probability(self,questionaire):

        self.km.set_evidence_from_questionaire(questionaire)

        return self.km.analyse_infection_probability()

def run(km,server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    handler_class.km = km
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()
