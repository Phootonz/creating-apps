import sys
import requests

def create_app(url, name, motto, secret):
    data = {
        "name": name,
        "motto": motto,
        "key": secret
    }
    update_app = requests.post(f'{url}/deploy', data=data)
    print(update_app)
    return update_app

if __name__ == "__main__":
    issue_body = sys.argv[1]
    secret = sys.argv[2]
    tokens = issue_body.split('\n')
    try:
        app_params = {item.split(':')[0]:item.split(':')[1].strip() for item in tokens}
    except IndexError:
        print("Some of your info was messed up")
        # output to error stream
    print(app_params)
    create_app(**app_params, secret=secret)
