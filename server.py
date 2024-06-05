# import requests
# response = requests.get("http://aosabook.org/en/500L/web-server/testpage.html")
# print(response.status_code)
# print(response.text)
from http.server import BaseHTTPRequestHandler,HTTPServer

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

    def send_page(self, page):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(bytes(page, encoding="utf8")) # must be sent back as bytes

    # serve a GET request
    def do_GET(self):
        page = self.create_page()
        self.send_page(page)

if __name__ == "__main__":
    serverAddress = ('', 8080) # run on current machine with this port
    server = HTTPServer(server_address=serverAddress, RequestHandlerClass=RequestHandler) # an HTTPServer class takes a server address(a port number) and a defined request handler
    server.serve_forever()
