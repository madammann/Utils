import re
import os

class ScriptWrapper:
    def __init__(self, script_path, wrapper_script, wrapper_name, repository_root_path, objects, arguments, main_func, main_arg):
        self.path = script_path
        self.repository_root_path = repository_root_path
        self.wrapper_script = wrapper_script
        self.wrapper_name = wrapper_name
        self.objects = objects
        self.arguments = arguments
        self.main_func = main_func
        self.main_arg = main_arg

        with open(self.path, 'r', encoding='ascii',errors='replace') as file:
            self.text = file.read()

    def write(self):
        with open(self.path,'w+', encoding='ascii',errors='replace') as file:
            file.write(self.text)

    def add_header(self):
        from_import = f'from {os.path.basename(self.wrapper_script)[:-3]} import {self.wrapper_name}{"," if self.objects != "" else ""}{self.objects}'
        header = f'import sys\nimport os\nsys.path.append(r"{self.repository_root_path}")\n{from_import}\n\n'

        self.text = header+self.text
        
    def add_wrapper(self):
        pattern = re.compile(r'(?m)^([ \t]*)def\s+[\w\_]+\s*([^\)])*|((\=\s*\()([\w\s\d,]+)(\)){1})\s*(\)*\s*->\s*\w+\s*)?:')
        self.text = re.sub(pattern, lambda match: f"{match.group(1) if match.group(1) != None else ''}@{self.wrapper_name}({self.arguments})\n{match.group(0)}", self.text)

    def order_wrappers(self):
        '''
        Reorders functions with multiple wrappers on top to have the wrapper function be the outer wrapper.
        '''
        pattern = re.compile(f'(?m)(^[\t ]*@(?!{self.wrapper_name}(?:\([^\n]*\n|\n))[^\n]*\n)(^[\t ]*@{self.wrapper_name}(\n|\([^\n]*\n))')

        self.text = re.sub(pattern, lambda match: f'{match.group(2)}{match.group(1)}', self.text)
        
        #slowly shifts the wrapper function to the top using regex
        while re.search(pattern, self.text) != None:
            self.text = re.sub(pattern, lambda match: f'{match.group(2)}{match.group(1)}', self.text)

    def is_main_candidate(self):
        #since we want to wrap the main function definition, we need to have it included and also assume path is in root dir of repository
        if re.search(re.compile(f'(def\s*{self.main_func}\()'), self.text) != None and os.path.dirname(self.path) == self.repository_root_path:
            return True
            
        return False

    def replace_directory_references(self):
        orig_rep = os.path.split(os.path.normpath(self.repository_root_path))[1][:-5]
        new_rep = os.path.split(os.path.normpath(self.repository_root_path))[1]
        
        pattern = re.compile(f'(?:[\"\']+)(?:[\w\:\.]*)(?:[\w\d\s\\\\/])*({orig_rep})(?:[\w\d\s\\\\/])*(?:[\"\']+)')

        self.text = re.sub(pattern, lambda match: f'{match.group(0).replace(orig_rep, new_rep)}', self.text)

    def process_main_function(self):
        '''
        We add the main_arg to the function with name wrapper_name, usually process=True is added to the wrapper over def main.
        '''
        pattern = re.compile(f'(?m)(@{self.wrapper_name}\()([^\)\(]*([^\)\(]*\([^\)\(]*\))*)(\)\n)((?:(?:@[^\n]*\n)*)|(?:@[^\n]*\n)*)(^[ \t]*def {self.main_func}\()')        
        self.text = re.sub(
            pattern,
            lambda match: f'{match.group(1)}{match.group(2)},{self.main_arg}{match.group(3) if match.group(3) != None else ""}{match.group(4) if match.group(4) != None else ""}{match.group(5) if match.group(5) != None else ""}{match.group(6)}',
            self.text
        )

        #in case the wrapper has only one argument we remove the comma
        self.text = self.text.replace(f"(,{self.main_arg}",f"({self.main_arg}")

    def verify_wrapping(self):
        func_matches = re.finditer(re.compile(f'(^[ \t]*def )'), self.text)
        wrapper_matches = re.finditer(re.compile(f'^[ \t]*@{self.wrapper_name}[^\n]*\n'), self.text)
        
        if len(list(func_matches)) == len(list(wrapper_matches)):
            return True

        #we find all functions without a wrapper function in front of them immediately after wrapping all function
        #(the possibility of multiwrapping functions without adding our own wrapper should be zero here, unless PEP guidelines are followed very VERY badly)
        unmatched_defs = []
        for fun in func_matches:
            if not any(fun.span()[0] == wra.span()[1]+1 for wra in wrapper_matches):
                #find the line of code in which the unwrapped function is to be found
                for i, line_match in enumerate(re.finditer(r'(?m)^[^\n]*',self.text)):
                    if fun.span()[0] in line_match.span():
                        unmatched_defs.append(i)

        print(f'Found possibly unmatched function defintions without the wrapper in lines: {",".join(unmatched_defs)} of {self.path}.')

        return False

    def wrap(self):
        self.replace_directory_references()
        self.add_header()
        self.add_wrapper()
        if not self.verify_wrapping():
            print('\nRemember to check these lines for possible errors of this script!!!\n')
        self.order_wrappers()

        if self.main_arg != "" and self.is_main_candidate():
            self.process_main_function()

