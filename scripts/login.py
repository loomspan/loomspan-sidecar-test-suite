"""Authorization Code + S256 PKCE, isolated browser sessions; no password grant."""
import environment as target_env
import base64, hashlib, http.server, json, pathlib, secrets, threading, urllib.parse, webbrowser
import httpx
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
ISSUER=target_env.url(18080, '/realms/equipment', 'localhost')
REDIRECT=target_env.url(18765, '/callback', 'localhost')
def login(user='maya',manual=False):
    verifier=secrets.token_urlsafe(48); state=secrets.token_urlsafe(24); received={}
    class Callback(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            params=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if params.get('state')!=[state]: self.send_error(400); return
            received.update(params); self.send_response(200); self.end_headers(); self.wfile.write(b'Login complete. You may close this tab.')
        def log_message(self,*args): pass
    server=http.server.HTTPServer(('127.0.0.1',target_env.port(18765)),Callback)
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    url=ISSUER+'/protocol/openid-connect/auth?'+urllib.parse.urlencode({
      'client_id':'equipment-browser','response_type':'code','scope':'openid','redirect_uri':REDIRECT,'state':state,
      'code_challenge':base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('='),'code_challenge_method':'S256'})
    try:
        if manual:
            import time
            webbrowser.open(url)
            deadline=time.monotonic()+180
            while 'code' not in received and time.monotonic()<deadline: time.sleep(.2)
        else:
            password=json.loads((ROOT/'.runtime/secrets.json').read_text())[user]
            with sync_playwright() as p:
                browser=p.chromium.launch()
                page=browser.new_page(); page.goto(url)
                page.locator('#username').fill(user); page.locator('#password').fill(password); page.locator('#kc-login').click()
                page.wait_for_url(REDIRECT+'*',timeout=30000); browser.close()
        if 'code' not in received: raise RuntimeError('PKCE callback missing')
        r=httpx.post(ISSUER+'/protocol/openid-connect/token',data={'grant_type':'authorization_code','client_id':'equipment-browser','code':received['code'][0],'redirect_uri':REDIRECT,'code_verifier':verifier},trust_env=False)
        r.raise_for_status(); return r.json()['access_token']
    finally: server.shutdown(); server.server_close()
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--manual',action='store_true'); parser.add_argument('--user',default='maya'); args=parser.parse_args()
    token=login(args.user,args.manual)
    path=ROOT/'.runtime'/f'{args.user}.token'; path.write_text(token)
    print('Access token saved in ignored .runtime directory; not printed.')
