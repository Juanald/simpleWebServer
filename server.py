# import requests
# response = requests.get("http://aosabook.org/en/500L/web-server/testpage.html")
# print(response.status_code)
# print(response.text)
from http.server import BaseHTTPRequestHandler,HTTPServer
import os

class RequestHandler(BaseHTTPRequestHandler):
    ''' Serving a basic page back to the user '''

    # This is the page we send back
    Page = '''\
<html>
<body>
<table>
<tr>  <td>Header</td>         <td>Value</td>          </tr>
<tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
<tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
<tr>  <td>Client port</td>    <td>{client_port}s</td> </tr>
<tr>  <td>Command</td>        <td>{command}</td>      </tr>
<tr>  <td>Path</td>           <td>{path}</td>         </tr>
</table>
</body>
</html>
'''
    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """
    def create_page(self):
        values = {
            # These are either standard Python functions or defined as instance variables for the BaseHTTPRequestHandler class
            'date_time'   : self.date_time_string(),
            'client_host' : self.client_address[0],
            'client_port' : self.client_address[1],
            'command'     : self.command,
            'path'        : self.path
        }
        page = self.Page.format(**values)
        return page

    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        # self.wfile.write(bytes(str(content), encoding="utf8")) # must be sent back as bytes
        self.wfile.write(content)

    # serve a GET request
    def do_GET(self):
        # page = self.create_page()
        # self.send_page(page)
        try:
            # figure out exactly what is being requested
            full_path = os.getcwd() + self.path
            print(full_path)

            # If we cannot find this file, we will raise a server exception
            if not os.path.exists(full_path):
                raise ServerException(f"{self.path} not found")
            
            # if a file, we handle it
            elif os.path.isfile(full_path):
                self.handle_file(full_path)
            
            else:
                raise ServerException(f"Unknown object {self.path}")
        
        except Exception as msg:
            self.handle_error(msg)
    
    def handle_file(self, full_path):
        ''' Handles a file, opens it, sends content'''
        try:
            with open(full_path, "rb") as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = f"{self.path} cannot be read: {msg}"
            self.handle_error(msg)
    
    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)


class ServerException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

if __name__ == "__main__":
    serverAddress = ('', 8080) # run on current machine with this port
    server = HTTPServer(server_address=serverAddress, RequestHandlerClass=RequestHandler) # an HTTPServer class takes a server address(a port number) and a defined request handler
    server.serve_forever()
