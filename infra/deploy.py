import sys

if __name__ == "__main__":
    issue_body = sys.argv[1]
    tokens = issue_body.split('\n')
    app_params = {item[0]:item[1] for item.split(':') in tokens}
    print(app_params)