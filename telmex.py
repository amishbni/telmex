import sys, os, csv
from bs4 import BeautifulSoup

colors = {
    "default": "\033[0m",
    "green": "\033[92m"
}

def extract(input_address, output_address):
    with open(input_address, 'r') as input_file, open(f"{output_address}.csv", 'a') as output_file:
        writer = csv.writer(output_file)
        soup = BeautifulSoup(input_file.read(), 'html.parser')
        messages = soup.select("div.message.default")
        from_name = ""
        reply_to = 0
        for message in messages:
            row = []
            row.append(int(message['id'].replace("message", "")))
            reply_to_div = message.select("div[class='body'] > div[class='reply_to details'] > a")
            if(reply_to_div):
                reply_to = int(reply_to_div[0]["href"].split("message")[-1])
            else:
                reply_to = 0
            row.append(reply_to)
            from_name_div = message.select("div[class='body'] > div.from_name")
            if(from_name_div):
                from_name = from_name_div[0].text.strip()
                if("via @" in from_name):
                    from_name = (from_name.split("via")[0]).strip()
            row.append(from_name)
            writer.writerow(row)

def main(dir_path):
    columns = ["message_id", "reply_to", "sender"]
    output_file_name = os.path.basename(os.path.normpath(dir_path))
    output_address = os.path.join(dir_path, output_file_name)
    with open(f"{output_address}.csv", 'a') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(columns)
    for file in os.listdir(dir_path):
        if(file.endswith(".html")):
            print(f"{colors['green']}➤ parsing {file}{colors['default']}")
            input_address = os.path.join(dir_path, file)
            extract(input_address, output_address)

if __name__ == "__main__":
    if(len(sys.argv) >= 2):
        main(sys.argv[1])
    else:
        print("Specify the path to data")
        sys.exit(1)
