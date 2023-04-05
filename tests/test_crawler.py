from tests.fixture import response_mocker, file_mocker, mock_response_obj
from crawler import crawler
from pytest_mock import mocker

expected_html = "<html><head><title>Test</title></head><body><a href='https://www.google.com'>Google</a><a href='https://www.google.com/search'>Search</a><a href='https://www.baidu.com'>baidu</a></body></html>"
expected_headers = {'Content-Type': 'text/html'}
google_url = 'https://www.google.com'
google_domain = 'www.google.com'

def test_hyper_ink_parser():
    parser = crawler.HyperlinkParser()
    parser.feed("<a href='https://www.google.com'>Google</a>")
    assert parser.hyperlinks == ["https://www.google.com"]

def test_get_hyperlinks_html():
    # act
    resp = mock_response_obj(expected_html, expected_headers)

    # Call the function being tested
    links = crawler.find_hyperlinks(resp)

    # Check that the links list contains the expected URL
    assert google_url in links

def test_get_hyperlinks_text():
    # act
    expected_headers_text = {'Content-Type': 'text/text'}
    resp = mock_response_obj(expected_html, expected_headers_text)

    # Call the function being tested
    links = crawler.find_hyperlinks(resp)

    # Check that the links list contains the expected URL
    assert links == []

def test_validate_domain_hyperlinks():
    # Call the function being tested
    links = crawler.validate_domain_hyperlinks(google_domain, [google_url])

    # Check that the links list contains the expected URL
    assert google_url in links

def test_validate_domain_hyperlinks_invalid_url():
    # Call the function being tested
    links = crawler.validate_domain_hyperlinks(google_domain, ['ftp://www.google.com'])

    # Check that the links list contains the expected URL
    assert links == []


def test_validate_domain_hyperlinks_different_domain():
    # Call the function being tested
    links = crawler.validate_domain_hyperlinks(google_domain, ['http://www.baidu.com'])

    # Check that the links list contains the expected URL
    assert links == []

def test_validate_domain_hyperlinks_relative_path():
    # Call the function being tested
    links = crawler.validate_domain_hyperlinks(google_domain, ['/search'])

    # Check that the links list contains the expected URL
    assert f'{google_url}/search' in links

def test_validate_domain_hyperlinks_relative_path_pound():
    # Call the function being tested
    links = crawler.validate_domain_hyperlinks(google_domain, ['#search'])

    # Check that the links list contains the expected URL
    assert links == []

def test_validate_domain_hyperlinks_suffix():
    # Call the function being tested
    links = crawler.validate_domain_hyperlinks(google_domain, [f'{google_url}/'])

    # Check that the links list contains the expected URL
    assert google_url in links

def test_crawl(mocker):
    # arrange

    # Mock the requests.get() method
    response = response_mocker(expected_html, expected_headers)
    mock_requests_get = mocker.patch('requests.get', return_value=response)

    # Mock the open() method
    file_obj = file_mocker('test.txt')
    mock_builtins_open = mocker.patch('builtins.open', return_value=file_obj)

    # act
    crawler.crawl(google_domain ,google_url)

    # assert
    expected = "TestGoogleSearchbaidu"
    assert file_obj.read() == expected
    assert mock_requests_get.call_count == 2
    assert mock_builtins_open.call_count == 2