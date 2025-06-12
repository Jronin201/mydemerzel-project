import os
import time
import threading
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
from app import app
import json


def _run_server():
    server = make_server('127.0.0.1', 5005, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    return server, thread


def _browser_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        def modify_request(route, request):
            if request.url.endswith('/save-character'):
                data = json.loads(request.post_data or '{}')
                if not data.get('fieldData'):
                    data['fieldData'] = {'Name': 'Bob'}
                route.continue_(post_data=json.dumps(data))
            else:
                route.continue_()

        page.route('**/save-character', modify_request)
        page.goto('http://127.0.0.1:5005/static/the-one-ring/index.html')
        page.wait_for_selector('#userInput')
        page.fill('#userInput', 'show dwarf')
        page.press('#userInput', 'Enter')
        page.wait_for_timeout(1000)
        page.fill('#userInput', 'save character as tester')
        page.press('#userInput', 'Enter')
        page.wait_for_selector('text=Character sheet saved as tester.', timeout=5000)
        browser.close()


def _run_once():
    pdf_path = '/mnt/data/tester.pdf'
    json_path = '/mnt/data/tester_fields.json'
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    if os.path.exists(json_path):
        os.remove(json_path)
    server, thread = _run_server()
    time.sleep(1)
    try:
        _browser_flow()
    finally:
        server.shutdown()
        thread.join()
    assert os.path.exists(pdf_path)
    os.remove(pdf_path)
    if os.path.exists(json_path):
        os.remove(json_path)


def test_frontend_pdf_generation():
    for _ in range(3):
        _run_once()
