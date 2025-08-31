import sys

if __name__ == "__main__":
    issue_body = sys.argv[1]
    tokens = issue_body.split('\n')
    app_params = {item.split(':')[0]:item.split(':')[1] for item in tokens}
    print(app_params)