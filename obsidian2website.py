import os, shutil, fileinput, re, hashlib
from variables import *

if __name__ == '__main__':

    print("[*] Welcome to Obsidian2Website")

    print("[*] Clearing output directory")
    for filename in os.listdir(posts_dest):
        file_path = os.path.join(posts_dest, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    print("[*] Clearing attachements directory")
    for filename in os.listdir(images_dest):
        file_path = os.path.join(images_dest, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    print("[*] Retrieving posts list")
    post_list = []
    for file in os.listdir(posts_source):
        if file.endswith(".md"):
            post_list.append(file)
    #print(f"[DEBUG] :", post_list)
    print(f"[+] Number of posts detected : {len(post_list)}")

    print("[*] Processing posts ...")
    for post in post_list:

        # Extract title and compute file name
        post_title = str(post).split('.', 1)[0]
        filename = post_title.replace(' ', '-').replace('é', 'e').replace('è', 'e').replace('à', 'a').replace('(', '').replace(')', '').replace(',', '').lower()

        # Copy and rename Markdown file in destination directory
        destination_path = os.path.join(posts_dest, "2000-01-01-" + filename + ".md")
        shutil.copyfile(os.path.join(posts_source, post), destination_path)

        # Parse markdown file (detect attachments and change filename, fix markdown, fix properties)
        attachments = []
        attachments_destination = ""
        is_in_properties = False
        with fileinput.input(files=destination_path, inplace=True, encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip('\n')

                if line == "---":
                    is_in_properties = not is_in_properties
                    print(line)
                    if is_in_properties:
                        print("title: " + post_title)

                # Fix properties (cover image)
                elif is_in_properties and line.startswith("title: "):
                    continue
                elif is_in_properties and line.startswith("path: "):
                    attachments.append(line.split(':')[1].strip(' '))
                    print("  path: " + hashlib.md5(attachments[-1].encode('utf-8')).hexdigest() + ".png")
                elif is_in_properties and line.startswith("alt: "):
                    print("  " + line)

                # Extract media directory
                elif is_in_properties and line.startswith("media_subpath: "):
                    attachments_destination = line.split(':')[1].strip(' ')
                    print("media_subpath: /assets/img/posts/" + attachments_destination)

                # Extract and rename attachements
                elif re.match(r'^!\[\[.*.png\]\]', line):
                    attachments.append(line.strip('!').strip('[').strip(']'))
                    print("![image](" + hashlib.md5(attachments[-1].encode('utf-8')).hexdigest() + ".png)")

                else:
                    print(line)

        # Debug
        #print(attachments)
        #print(attachments_destination)

        # Create attachement directory
        image_newdir = os.path.join(images_dest, attachments_destination)
        if not os.path.isdir(image_newdir):
            os.mkdir(image_newdir)

        # Copy and rename attachements in the new directory
        if len(attachments) > 0:
            for image in attachments:
                image_path = os.path.join(images_source, image)
                image_newname = hashlib.md5(image.encode('utf-8')).hexdigest() + ".png"
                images_out = os.path.join(image_newdir, image_newname)

                if not os.path.isfile(images_out):
                    shutil.copyfile(image_path, images_out)

    print("[+] Processing sucessfully completed")