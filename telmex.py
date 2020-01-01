import sys, os
from bs4 import BeautifulSoup

colors = {
    "default": "\033[0m",
    "green": "\033[92m"
}

def extract(file_path):
    with open(file_path, 'r') as ofile:
        soup = BeautifulSoup(ofile.read(), 'html.parser')
        messages = soup.find_all("div", ["message", "default"])
        print(f"    {len(messages)} messages")

def main(dir_path):
    for file in os.listdir(dir_path):
        if(file.endswith(".html")):
            print(f"{colors['green']}➤ parsing {file}{colors['default']}")
            extract(os.path.join(dir_path, file))

if __name__ == "__main__":
    if(len(sys.argv) >= 2):
        main(sys.argv[1])
    else:
        print("Specify the path to data")
        sys.exit(1)
