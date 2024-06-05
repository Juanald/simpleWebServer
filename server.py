# import requests
# response = requests.get("http://aosabook.org/en/500L/web-server/testpage.html")
# print(response.status_code)
# print(response.text)
from http.server import BaseHTTPRequestHandler,HTTPServer
import os

"Each one of these classes implement a test and action, action to be executed if the test is true"
class case_no_file(object):
    '''File or directory does not exist'''
    def test(self, handler):
        return not os.path.exists(handler.full_path)
    
    def act(self, handler):
        raise ServerException(f"{handler.path} not found") # what is this handler?
    
class case_existing_file(object):
    '''Case of file existing'''
    def test(self, handler):
        return os.path.isfile(handler.full_path)
    
    def act(self, handler):
        handler.handle_file(handler.full_path)

class case_always_fail(object):
    '''Case of file existing'''
    def test(self, handler):
        True
    
    def act(self, handler):
        raise ServerException(f"Unknown object: {handler.full_path}")

class case_directory_index_file(object):
    '''In case there is an index file in a certain directory, serve that index.html'''
    def index_path(self, handler):
        # Function that just joins together to form a potential path to a potential index.html
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))
    
    def act(self, handler):
        handler.handle_file(self.index_path(handler))

class case_directory_no_index_file(object):
    '''Directory path, index file does not exist, action is to show listing'''
    def index_path(self, handler):
        # Function that just joins together to form a potential path to a potential index.html
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and not os.path.isfile(self.index_path(handler))
    
    def act(self, handler):
        '''We want to list directory contents'''

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
    Listing_Page = """\
        <html>
        <body>
        <ul>
        {0}
        </ul>
        </body>
        </html>
        """
    
    def show_listing_page(self, full_path):
        '''Function shows the listing page, called in case a directory is accessed with no index.html file'''
        try:
            entries = os.listdir(full_path)
            bullets = ["<li>{e}</li>" for e in entries if not e.startswith(".")] # list comprehension to fill <li></li> elements
            page = self.Listing_Page.format('\n'.join(bullets)) # bullets is a list, join at a newline
            self.send_content(page)
        except OSError as msg:
            msg = "{self.path} cannot be found: {msg}"
            self.handle_error(msg)

    
    # This acts like an enum
    Cases = [case_no_file(), case_existing_file(), case_directory_index_file(), case_always_fail()]
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

            # # If we cannot find this file, we will raise a server exception
            # if not os.path.exists(full_path):
            #     raise ServerException(f"{self.path} not found")
            
            # # if a file, we handle it
            # elif os.path.isfile(full_path):
            #     self.handle_file(full_path)
            
            # else:
            #     raise ServerException(f"Unknown object {self.path}")
            for case in self.Cases:
                handler = case()
                # Why do we have to add a self here?
                if handler.test(self):
                    handler.act(self)
                    break

        
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
