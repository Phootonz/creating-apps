import sys

if __name__ == "__main__":
    issue_body = sys.argv[1]
    tokens = issue_body.split('\n')
    for token in tokens:
        print(token)