from tqdm import tqdm
import argparse
import os

from os_operations import copy_respository, grab_file_and_folders, grab_all_python_scripts, copy_file
from reg_exp import ScriptWrapper

parser = argparse.ArgumentParser(
    prog='RepositoryWrapper',
    description='Enables the wrapping of all function of a python repository with a single command line.',
    epilog=''
)

#required arguments
parser.add_argument('folder', default='./repository/', type=str, help='Absolute path to the repository folder you which to wrap.')
parser.add_argument('wrapper_func', default='', type=str, help='Name of the wrapper function to use from the wrapper script.')

#optional arguments
parser.add_argument('-ws','--wrapper_script', default='wrapper.py', type=str, help='Name of the script containing the wrappers placed inside this folder in the repository.')
parser.add_argument('-wa','--wrapper_arguments', default='', type=str, help='String containing the exact arguments inside the brackets of the wrapper to be used everywhere.')
parser.add_argument('-obj','--objects', default='', type=str, help='String defining the objects as if writing in code to be ')
parser.add_argument('-c','--composite', default=False, type=bool, help='Boolean flag whether to analyse almost every line of code instead of every function only.')
parser.add_argument('-mf','--main_func', default='main', type=str, help='The name of the main function of the repository, usually unecessary argument.')
parser.add_argument('-ma','--main_arg', default='process=True', type=str, help='The literal keyword argument to pass to the wrapper of the main function, only needed with custom wrappers.')

def main():
    args, unknown_args = parser.parse_known_args()
    print(f'Wrapping Python scripts in {args.folder} with function {args.wrapper_func}.\n')

    #use wrapper arguments defaulted to wrapper func in case wrapper func is not custom wrapper but known
    known_wrappers = ['tmpfile_timer', 'tmpfile_monitor']
    wrapper_arguments = args.wrapper_arguments
    objects = args.objects
    main_func_arg = args.main_arg
    
    if not args.wrapper_func in known_wrappers and args.wrapper_arguments == '':
        raise ValueError('Wrapper arguments are required to pass in command prompt when using custom wrapper functions.')

    #case by case default arguments
    if args.wrapper_func == 'tmpfile_timer' and wrapper_arguments == '' and objects == '':
        wrapper_arguments = 'tmp_path'
        objects = 'tmp_path'
        main_func_arg = 'process=True'

        print(f'Wrapper arguments and imported objects defaulting for {args.wrapper_func} to: {wrapper_arguments} and {objects}.\n')

    if args.wrapper_func == 'tmpfile_monitor':
        if args.wrapper_arguments == '':
            raise ValueError("Requires wrapper arguments for tmpfile path and also list of function names to watch in format: \"tmp_path,f=[\"func_a\",\"func_b\",...]\"")
        objects = 'tmp_path'
        main_func_arg = 'process=True'
        
    #first copy entire repository
    copy_path = copy_respository(args.folder)

    #find all python scripts in copied repo
    scripts = grab_all_python_scripts(copy_path)

    #we copy the wrapper script into the copied repo
    copy_file(os.path.abspath(args.wrapper_script), os.path.join(copy_path, args.wrapper_script))

    #we wrap and add imports in every python script in the repository
    s_wrappers = [
        ScriptWrapper(
            script, args.wrapper_script, args.wrapper_func, copy_path, objects, wrapper_arguments, args.main_func , main_func_arg
        ) for script in scripts if not script.endswith(args.wrapper_script)
    ]

    for w in s_wrappers:
        try:
            w.wrap()
            
        except Exception as e:
            print(e)
            print(
                f'Ran into a problem trying to wrap the script {w.path} with function {args.wrapper_func}({args.wrapper_arguments}).'
                f'Look up the required arguments and manually wrap the script yourself by having a look into the errorlessly wrapped scripts.\n'
            )
        w.write()

if __name__ == "__main__":
    main()