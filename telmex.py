import sys, os, csv
from bs4 import BeautifulSoup
from datetime import datetime as dt

colors = {
    "default": "\033[0m",
    "green": "\033[92m"
}

def extract(input_address, output_address):
    with open(input_address, 'r') as input_file, open(f"{output_address}.csv", 'a') as output_file:
        writer = csv.writer(output_file)
        soup = BeautifulSoup(input_file.read(), 'html.parser')
        messages = soup.select("div.message.default")
        from_name, message_type = [""]*2
        reply_to, message_date = [0]*2
        for message in messages:
            row = []

            # message_id
            row.append(int(message['id'].replace("message", "")))

            # reply_to
            reply_to_div = message.select("div[class='body'] > div[class='reply_to details'] > a")
            if(reply_to_div):
                reply_to = int(reply_to_div[0]["href"].split("message")[-1])
            else:
                reply_to = 0
            row.append(reply_to)

            # sender
            from_name_div = message.select("div[class='body'] > div.from_name")
            if(from_name_div):
                from_name = from_name_div[0].text.strip()
                if("via @" in from_name):
                    from_name = (from_name.split("via")[0]).strip()
            row.append(from_name)

            # message_type
            message_type_div = message.select("div.body > div.media_wrap > div.media")
            if(message_type_div):
                message_type = message_type_div[0]["class"][-1].replace("media_", "")
                if(message_type in ["photo", "video"]):
                    message_type = message_type_div[0].select("div.body > div.title")[0].text.lower()
                if(message_type in ["audio_file", "voice_message"]):
                    message_type = message_type.split("_")[0]
                message_type = message_type.strip()
            else:
                message_type = "text"
            row.append(message_type)

            # message_date
            date_div = message.select("div[class='body'] > div.date")
            if(date_div):
                message_date = int(dt.strptime(date_div[0]["title"], "%d.%m.%Y %H:%M:%S").strftime("%s"))
            row.append(message_date)
            writer.writerow(row)

def main(dir_path):
    columns = ["message_id", "reply_to", "sender", "message_type", "message_date"]
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
