import requests
import shutil
import json
import tarfile
import os
import re

# Disable running as root.
if os.geteuid() == 0:
    print("You are not allowed to run this script as root. Please run as a normal user.")
    exit()

home = os.getenv("HOME")

# Check if proton folder exists, make one if it does not.
path = home + "/.steam/root/compatibilitytools.d/"
if os.path.isdir(path) == True:
    print("Proton folder exists. ({})".format(path))
else:
    print("Proton folder does not exist. Creating...")
    try:
        os.makedirs(path)
        print("Proton folder created. ({})".format(path))
    except Exception as e:
        print("Error creating Proton folder.")
        exit()

# Get the file
r = requests.get("https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest").text
j = json.loads(r)

download_url=j["assets"][1]["browser_download_url"]
version_number = re.findall(r'[^/]+(?=/$|$)',download_url)
save_location = os.path.join(path,version_number[0])
folder_name = version_number[0].replace(".tar.gz","")
folder_loc = os.path.join(path+folder_name)

# Also check if you already have it
def already_exists():
    if os.path.isdir(folder_loc):
        print("Latest version already installed. Would you like to delete it and re-download it? [y/n]")
        delete_file = str(input()).lower()
        if delete_file == "y":
            print("Removing folder...")
            shutil.rmtree(folder_loc)
        elif delete_file == "n":
            print("Cancelled by user")
            exit(0)
        else:
            print("Invalid input.")
            return already_exists()
    else:
        pass

already_exists()    

print("Downloading {}".format(version_number[0]))

proton_file = requests.get(download_url,allow_redirects=True)
with open(save_location,"wb") as f:
    f.write(proton_file.content)

print("File downloaded.")

# Extract the file
print("Extracting...")
with tarfile.open(save_location) as proton_tar:
    def is_within_directory(directory, target):
        
        abs_directory = os.path.abspath(directory)
        abs_target = os.path.abspath(target)
    
        prefix = os.path.commonprefix([abs_directory, abs_target])
        
        return prefix == abs_directory
    
    def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
    
        for member in tar.getmembers():
            member_path = os.path.join(path, member.name)
            if not is_within_directory(path, member_path):
                raise Exception("Attempted Path Traversal in Tar File")
    
        tar.extractall(path, members, numeric_owner=numeric_owner) 
        
    
    safe_extract(proton_tar, folder_loc)
    proton_tar.close()
print("Extracted.")

# Remove subdirectoy
print("Removing subdirectory...")
try:
    os.rename(folder_loc,folder_loc+"_")
    shutil.move(os.path.join(folder_loc+"_",folder_name),folder_loc)
    shutil.rmtree(os.path.join(folder_loc+"_"))
except Exception as e:
    print("Error removing subdirectory")
    exit()
print("Subdirectory removed.")

# Remove tarfile
print("Removing tarfile...")
try:
    os.remove(save_location)
except Exception as e:
    print("Error removing tarfile.")
    exit()
print("Tarfile removed.")

# Done
print("Done.")