import sys, os, csv
from bs4 import BeautifulSoup
from datetime import datetime as dt
import pandas as pd

colors = {
    "default": "\033[0m",
    "green": "\033[92m"
}

def reply_to_sender(data, reply_to_id):
    if(reply_to_id != 0):
        reply_to_sender_values = data.loc[data["message_id"] == reply_to_id]["sender"].values
        if len(reply_to_sender_values) == 1:
            return reply_to_sender_values[0]
        else:
            return ""
    else:
        return ""

def create_reply_to_sender(output_address):
    data = pd.read_csv(output_address)
    data.insert(loc=3, column="reply_to_sender", value=data["reply_to_id"].apply(lambda x: reply_to_sender(data, x)))
    data.to_csv(output_address, encoding='utf-8', index=False)

def post_process(output_address):
    print(f"→ creating new column, {colors['green']}reply_to_sender{colors['default']}")
    create_reply_to_sender(output_address)

def to_seconds(time_string):
    minutes, seconds = time_string.split(":")
    return (int(minutes) * 60) + int(seconds)

def to_KB(media_size_string):
    media_size, size_format = media_size_string.split(' ')
    if(size_format == "GB"):
        return float(media_size.strip())*1000000
    elif(size_format == "MB"):
        return float(media_size.strip())*1000
    elif(size_format == "B"):
        return float(media_size.strip())/1000
    else:
        return float(media_size.strip())

def extract(input_address, output_address):
    with open(input_address, 'r') as input_file, open(f"{output_address}.csv", 'a') as output_file:
        writer = csv.writer(output_file)
        soup = BeautifulSoup(input_file.read(), 'html.parser')
        messages = soup.select("div.message.default")
        from_name, message_type, forwarded_from, caption, text = [""]*5
        media_size, photo_resolution, sticker_emoji = [""]*3
        reply_to_id, message_date, is_forwarded, media_duration = [0]*4
        for message in messages:
            row = []

            # message_id
            row.append(int(message['id'].replace("message", "")))

            # reply_to_id
            reply_to_id_div = message.select("div[class='body'] > div[class='reply_to details'] > a")
            if(reply_to_id_div):
                reply_to_id = int(reply_to_id_div[0]["href"].split("message")[-1])
            else:
                reply_to_id = 0
            row.append(reply_to_id)

            # sender
            from_name_div = message.select("div[class='body'] > div.from_name")
            if(from_name_div):
                from_name = from_name_div[0].text.strip()
                if("via @" in from_name):
                    from_name = (from_name.split("via")[0]).strip()
            row.append(from_name)

            # message_type
            message_type_div = message.select("div.body > div.media_wrap > div.media")
            text_or_caption_div = message.select("div[class='body'] > div[class='text']")
            if(message_type_div):
                message_type = message_type_div[0]["class"][-1].replace("media_", "")
                if(message_type in ["photo", "video"]):
                    message_type = message_type_div[0].select("div.body > div.title")[0].text.lower()
                if(message_type in ["audio_file", "voice_message"]):
                    message_type = message_type.split("_")[0]
                message_type = message_type.strip()
                text = ""
                if(text_or_caption_div):
                    caption = text_or_caption_div[0].text.strip()
                else:
                    caption = ""
            else:
                message_type = "text"
                caption = ""
                if(text_or_caption_div):
                    text = text_or_caption_div[0].text.strip()
                else:
                    text = ""
            row.append(message_type)

            # message_date
            date_div = message.select("div[class='body'] > div.date")
            if(date_div):
                message_date = int(dt.strptime(date_div[0]["title"], "%d.%m.%Y %H:%M:%S").strftime("%s"))
            row.append(message_date)

            # is_forwarded
            is_forwarded_div = message.select("div.forwarded")
            if(is_forwarded_div):
                is_forwarded = 1
            else:
                is_forwarded = 0
            row.append(is_forwarded)

            # forwarded_from
            forwarded_from_div = message.select("div[class='body'] > div[class='forwarded body'] > div[class='from_name']")
            if(forwarded_from_div):
                for span in forwarded_from_div[0].find_all("span"):
                    span.extract()
                forwarded_from = forwarded_from_div[0].text.strip()
            else:
                forwarded_from = ""
            row.append(forwarded_from)

            # text and caption
            row.append(text)
            row.append(caption)

            # media details
            media_details_div = message.select("div.body > div.media_wrap > div.media > div.body > div[class='status details']")
            if(media_details_div):
                media_details = media_details_div[0].text.strip().split(',')
                if(len(media_details) == 1):
                    if(message_type == "contact"):
                        media_size = ""
                    else:
                        media_size = media_details[0].strip()
                    photo_resolution, sticker_emoji = [""]*2
                    media_duration = 0
                else:
                    if(":" in media_details[0]):
                        media_duration = to_seconds(media_details[0].strip())
                        sticker_emoji, photo_resolution = [""]*2
                    elif("x" in media_details[0]):
                        photo_resolution = media_details[0].strip()
                        sticker_emoji = ""
                        media_duration = 0
                    else:
                        sticker_emoji = media_details[0].strip()
                        photo_resolution = ""
                        media_duration = 0
                    media_size = media_details[1].strip()

                if(media_size):
                    media_size = to_KB(media_size)
            else:
                media_size, photo_resolution, sticker_emoji = [""]*3
                media_duration = 0

            row.extend([media_size, photo_resolution, media_duration, sticker_emoji])
            writer.writerow(row)

def main(dir_path):
    columns = ["message_id", "reply_to_id", "sender", "message_type", "message_date", "is_forwarded",
            "forwarded_from", "text", "caption", "media_size", "photo_resolution", "media_duration", "sticker_emoji"]
    output_file_name = os.path.basename(os.path.normpath(dir_path))
    output_address = os.path.join(dir_path, output_file_name)
    with open(f"{output_address}.csv", 'a') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(columns)
    for file in os.listdir(dir_path):
        if(file.endswith(".html")):
            sys.stdout.write('\033[2K\033[1G')
            print(f"→ parsing {colors['green']}{file}{colors['default']}", end='\r')
            input_address = os.path.join(dir_path, file)
            extract(input_address, output_address)
    print()
    post_process(f"{output_address}.csv")

if __name__ == "__main__":
    if(len(sys.argv) >= 2):
        main(sys.argv[1])
    else:
        print("Specify the path to data")
        sys.exit(1)
