from http.server import HTTPServer,BaseHTTPRequestHandler
import json
import service_episodic_memory
Host="127.0.0.1"
PORT=9998
class NeuralHTTP(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_GET(self):
        self._set_headers()
        respose={"text":"Hello peter"}
        # respose="<html><head> </head> <body><h1>Hello World<h1> </body></html>"
        self.wfile.write(bytes(str(respose),"utf-8"))

    def do_POST(self):
        self._set_headers()
        data_len = int(self.headers['Content-Length'])
        data = self.rfile.read(data_len)
        obj_dict=json.loads(data)
        previous_statements=obj_dict["previous_statements"]
        query=obj_dict["query"]
        # print(query+"\n"+str(previous_statements))
        res=service_episodic_memory.evalute_result(previous_statements,query)
        self.wfile.write(bytes(str(res),'utf-8'))

    


server= HTTPServer((Host,PORT),NeuralHTTP)  
print("Server now running..\n and port is 9998 \n running on 127.0.0.1")
server.serve_forever()
server.server_close()  
print("Server stopped!!")