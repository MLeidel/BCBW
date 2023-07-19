# fixurls.py
# use to convert descq urls.txt to bcb urls.txt file
# remove [<=> ] from urls.txx
# and write just the url to urls.txt

fout = open("urls.txt", "w")

with open("urls.txx", "rb") as fin:
    for line in fin:
        url = line.decode().strip()
        if url.startswith("http"):
            fout.write(url)
        else:
            fout.write(url.split("<=> ")[1] + "\n")
fout.close()
