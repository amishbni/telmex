import sys, os, csv
from bs4 import BeautifulSoup

colors = {
    "default": "\033[0m",
    "green": "\033[92m"
}

def extract(file_path, output_file_name):
    with open(file_path, 'r') as out_file, open(f"{output_file_name}.csv", 'a') as in_file:
        writer = csv.writer(in_file)
        soup = BeautifulSoup(out_file.read(), 'html.parser')
        messages = soup.select("div.message.default")
        from_name = ""
        for message in messages:
            row = []
            row.append(message['id'])
            from_name_div = message.select("div.body > div.from_name")
            if(from_name_div):
                from_name = from_name_div[0].text.strip()
            row.append(from_name)
            writer.writerow(row)
def main(dir_path):
    for file in os.listdir(dir_path):
        if(file.endswith(".html")):
            print(f"{colors['green']}➤ parsing {file}{colors['default']}")
            output_file_name = os.path.basename(os.path.normpath(dir_path))
            extract(os.path.join(dir_path, file), output_file_name)

if __name__ == "__main__":
    if(len(sys.argv) >= 2):
        main(sys.argv[1])
    else:
        print("Specify the path to data")
        sys.exit(1)
