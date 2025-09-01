import sys
import requests

def update_status(url, name, status, secret):
    data = {
        "name": name,
        "status": status,
        "key": secret
    }
    headers = {'Content-Type':'application/json'}
    print(data)
    update_app = requests.post(f'{url}/status', data=data, headers=headers)
    update_app.raise_for_status()
    return update_app

if __name__ == "__main__":
    status = sys.argv[1]
    issue_body = sys.argv[2]
    secret = sys.argv[3]

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
    update_status(app_params.get("url"), app_params.get("name"), status, secret)