import sys
import requests

def create_app(url, name, motto, secret):
    data = {
        "name": name,
        "motto": motto,
        "key": secret
    }
    headers = {'Content-Type':'application/json'}
    update_app = requests.post(f'{url}/deploy', json=data, headers=headers)
    update_app.raise_for_status()
    return update_app

if __name__ == "__main__":
    issue_body = sys.argv[1]
    secret = sys.argv[2]
    tokens = issue_body.split('\n')
    print(f"issue tokens: {tokens}")
    try:
        app_params = {}
        for item in tokens:
            if ':' in item:
                key,value = item.split(":", 1)
                app_params[key.strip()] = value.strip()
    except IndexError:
        print("Some of your info was messed up")
        # output to error stream

    create_app(app_params.get('name'), app_params.get('motto'), app_params.get('url'), secret=secret)
