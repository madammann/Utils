# Repository Wrapper
This repository contains a script which takes in the path of a directory with python scripts and creates a copy of it with every function wrapped in a wrapper function defined here.  

---
## Usage
For using this repository, all that is required is a working installation around python 3.7-3.12, others will likely also work.  
Depending on the operating system problems may arise though, but for Windows it should work fine.  
In addition the requirements need to be installed in order to use all prewritten functions.  

Running the script works from command easily using the following line with the required arguments folder and wrapper_func.  
The argument folder takes the path to the directory of the repository, wrapper_func takes in the exact name of the wrapper function to use.  
``
python main.py --folder='path' --wrapper_func='wrapper'
``

After running check the functionality of your repository and the command log for exceptions which include documents which may need manual wrapping.  
In addition, and function that is called \_\_main\_\_ and in a module named \_\_main\_\_ will get an additional argument process=True into it's wrapper.  
**This means if you do not have a main function in main you need to write this argument yourself to ensure the wrapper properly processes the data!**  

1. The name of the wrapper function which you wish to use:  
``
--wrapper_script='path/script.py'
``  

2. Exact string to pass to all wrapper functions (including passed objects, see 4):  
``
--wrapper_arguments='a=20,b=object'
``  

3. Objects to import to every script from the wrapper script (see 2) as comma-separated list:  
``
--objects='object_a, object_b'
``  

4. Whether to break apart almost all lines into separate functions to analyse with wrapper (experimental, not implemented yet):  
``
--composite=True
``

---
## Wrappers
### timer
This wrapper measures execution time using datetime.datetime.now() before and after function runtime.  
It does not consider it's own runtime and thereby running the wrapper will introduce some inaccuracies in and of itself, depending on log object it can also create a memory footprint or worsen the accuracy further if drive writing is performed.  

For optimal accuracy run in [standard execution](#standard-execution).  
Multithreading is supported but results in low accuracy for specific functions, since multithreading may multitask on different functions at the same time whilst awaiting a computation result.  
Multiprocessing is supported only on multiprocessing-safe objects, as can be read in the function docstring.  
Iintuitively use the following:
#### Standard execution (change path to desired repository)
``
python main.py --folder='path' --wrapper_func='timer' --wrapper_arguments='log_list' --objects='log_list'
``
#### Multithreaded execution (change path to desired repository)
``
python main.py --folder='path' --wrapper_func='timer' --wrapper_arguments='log_list' --objects='log_list'
``
#### Multiprocessing execution (change path to desired repository)
``
python main.py --folder='path' --wrapper_func='timer' --wrapper_arguments='log_mparray' --objects='log_list'
``

---
## Custom wrappers
Feel free to implement your custom wrapper and also share it.  
The only requirement is that the custom wrapper takes at least the keyword argument ``process=False : bool``.  
This is required for running it properly by enabling a modus for finalization after main in main.py is ran.  

---
## Support
There is, depending on used functionalities of you repository, a limitation on what works and does not work.  
Theoretically, with your own custom wrapper function no problems should arise.  
Conflicts with multiwrapped functions have not been tested such as tf.function wrappers for example.  
Also for following execution modes I have added information on the limitations and capabilities of the wrappers included in wrapper.py.  

### Standard execution
With standard execution you can simply use datatypes such as lists and dictionaries without issue.  
Here really anything goes.  

### Multiprocessed execution
For multiprocessed execution there are issues with unshared memory requiring you to use multiprocessing arrays that are filled for shared memory, or memory-mapped files, or, alternatively simply a file opened in append mode.  
Lists, dictionaries, and other native python objects **will** not work and not get updated in other processes.  

### Multithreaded execution
For multithreaded execution the same rules as standard work, unless when combined with multiprocessing.  
You may use any datatype freely, however, remember that the execution order of code snippets gets changed in multithreading meaning accuracy and order both suffer for measurements.  

### HPC execution
Depending on the cluster there may be problems running specific wrappers due to either memory communication in several unconnected nodes or other features.  
But everything should and will work with the right wrapper, you just need to find a good wrapper and a finilization function.  

---
## Contact
[Marlon Dammann](mdammann@uni-osnabrueck.de)