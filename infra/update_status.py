import sys
import requests

def update_status(url, name, status, secret):
    data = {
        "name": name,
        "status": status,
        "key": secret
    }
    update_app = requests.post(f'{url}/status', data=data)
    update_app.raise_for_status()
    return update_app

if __name__ == "__main__":
    status = sys.argv[1]
    issue_body = sys.argv[2]
    secret = sys.argv[3]

    tokens = issue_body.split('\n')
    print(tokens)
    try:
        app_params = {item.split(':')[0]:item.split(':')[1].strip() for item in tokens}
    except IndexError:
        print("Some of your info was messed up")
        # output to error stream
    update_status(app_params.get("url"), app_params.get("name"), status, secret)