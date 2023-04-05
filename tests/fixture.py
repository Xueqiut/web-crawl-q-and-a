import contextlib
import pytest

'''
This file contains the mock response class that is used to mock the response
from the urlopen() function in the crawler.py file.
html: The HTML response, which is a string
headers: The headers of the response, which is a dictionary
'''
class response_mocker(contextlib.AbstractContextManager):
    def __init__(self, html, headers):
        self.text = html
        self.headers = headers
    
    def __enter__(self):
        return self
    
    # no implementation of __exit__ is required
    def __exit__(self, exc_type, exc_value, traceback):
        pass

def mock_response_obj(expected_html, expected_headers):
    return response_mocker(expected_html, expected_headers)

class file_mocker(contextlib.AbstractContextManager):
    def __init__(self, file_name):
        self.file_name = file_name
    
    def write(self, text):
        self.buffer += text

    def read(self):
        return self.buffer
    
    def __enter__(self):
        self.buffer = ""
        return self
    
    # no implementation of __exit__ is required
    def __exit__(self, exc_type, exc_value, traceback):
        pass

@pytest.fixture(autouse=True)
def stop_mock():
    mocker.stopall()