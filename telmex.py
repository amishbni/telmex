import sys, os

def main(data_path):
    for file in os.listdir(data_path):
        if(file.endswith(".html")):
            print(file)

if __name__ == "__main__":
    if(len(sys.argv) >= 2):
        main(sys.argv[1])
    else:
        print("Specify the path to data")
        sys.exit(1)
