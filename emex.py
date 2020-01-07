import emoji, regex

def emex(text):
    emojis = []
    data = regex.findall(r"\X", text)
    for grapheme in data:
        if any(char in emoji.UNICODE_EMOJI for char in grapheme):
            emojis.append(grapheme)

    # flags
    emojis.extend(regex.findall(u"\uD83C[\uDDE6-\uDDFF]", text))
    return emojis
