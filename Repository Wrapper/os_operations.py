import os

def grab_all_python_scripts(path):
    script_list = []
    for p in os.listdir(path):
        if p.endswith('.py') and os.path.isfile(os.path.join(path, p)):
            script_list += [os.path.join(path, p)]
        elif os.path.isdir(os.path.join(path, p)):
            script_list += grab_all_python_scripts(os.path.join(path, p))

    return script_list

def grab_file_and_folders(path):
    file_list, folder_list = [], []
    if os.path.isfile(path):
        file_list += [path]
    else:
        folder_list += [path]
        for p in os.listdir(path):
            res = grab_file_and_folders(os.path.join(path, p))
            file_list += res[0]
            folder_list += res[1]

    return file_list, folder_list

def copy_respository(path : str) -> None:
    '''
    Copies an entire folder and the file contents of it in the same directory with the suffix "_copy".
    
    Args:
        path (str): The absolute folder path of the source folder. 
    '''
    copy_path = os.path.abspath(path) + '_copy'
    os.makedirs(copy_path,exist_ok=True)
    
    files, folders = grab_file_and_folders(path)

    folders = [os.path.abspath(path)+'_copy'+folder[folder.find(path)+len(path):] for folder in folders]
    dest_files = [os.path.join(os.path.abspath(path).rstrip('\\')+'_copy',file[file.find(path)+len(path):].lstrip('\\')) for file in files]

    for folder in folders:
        os.makedirs(folder,exist_ok=True)

    for source, target in zip(files, dest_files):
        copy_file(source, target)

    return copy_path

def copy_file(src, dest):
    with open(src, 'rb') as file:
        with open(dest, 'wb+') as copy:
            copy.write(file.read())