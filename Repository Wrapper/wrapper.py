import os
import time
import string
import random
import tempfile

import multiprocessing as mp
import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from functools import wraps
from copy import deepcopy

from wrapper_utils import ObjectWrapper

#multiprocessing arrays get generated automatically by script when functionality added HERE
# log_array = multiprocessing.Array

#Objects which may be imported as shared data structures
tmp_path = os.path.join(tempfile.gettempdir(),f'tmpfile_RepositoryWrapper_log.tmp')

#Multiprocessing unsafe:
log_list = []
log_dict = dict()

#Multiprocessing-safe:
log_mparray = None

def tmpfile_timer(path : str, process=False):
    '''
    Wrapper function for analysing the speed of functions.
    Accuracy decreases over execution time and in functions with many function calls inside, but should still remain relatively accurate.
    Uses temporary files to collect data during function execution.

    param:
        path (str): The path to the location where the temorary file is to be created.
        process (bool): Whether to process the entire data into a dataframe once the execution is over, default behavior of this script enables this when running a function called main.
    '''
    
    def outer(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            start_time = time.time_ns()
            response = fn(*args, **kwargs)
            end_time = time.time_ns()

            with open(path, 'a+') as file:
                file.write(f'{fn.__module__},{fn.__name__},{end_time - start_time}\n')

            if process:
                with open(path, 'r') as file:
                    data = [line.split(',') for line in file.read().split('\n')]
                    data = [datum for datum in data if len(datum) == 3]
                    df = pd.DataFrame(data,columns=['Module', 'Function', 'ns'])
                    
                    df['ns'] = df['ns'].astype('int64')
                    
                    df['TIME'] = pd.to_timedelta(df['ns'], unit='ns')
                    df['Hours'] = df['TIME'].dt.components.hours
                    df['Minutes'] = df['TIME'].dt.components.minutes
                    df['Seconds'] = df['TIME'].dt.components.seconds
                    df['Microseconds'] = df['TIME'].dt.components.microseconds
                    df['Nanoseconds'] = df['TIME'].dt.components.nanoseconds
                    df = df.drop(columns=['TIME'])

                    df = df.groupby(['Module','Function']).agg(
                        Executions=('ns', 'size'),
                        Hours=('Hours', 'mean'),
                        Minutes=('Minutes', 'mean'),
                        Seconds=('Seconds', 'mean'),
                        Microseconds=('Microseconds', 'mean'),
                        Nanoseconds=('Nanoseconds', 'mean')
                    ).reset_index()

                    df.to_csv('./tmpfile_timer_results.csv',index=None)

                with open(path, 'w') as file:
                    file.write('')

                os.unlink(path)
            
            return response
            
        return inner
        
    return outer

def func_isolator(path : str, func_name : str, process=False):
    '''
    Wrapper function for analysing the speed of functions.
    Accuracy decreases over execution time and in functions with many function calls inside, but should still remain relatively accurate.
    Uses temporary files to collect data during function execution.

    param:
        path (str): The path to the location where the temorary file is to be created.
        process (bool): Whether to process the entire data into a dataframe once the execution is over, default behavior of this script enables this when running a function called main.
    '''
            
    def outer(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            arg_str = [str(ObjectWrapper(arg) for arg in args])
            kwarg_str = [str(ObjectWrapper(kwarg) for kwarg in kwargs])
            
            response = fn(*args, **kwargs)
            
            res_str = str(ObjectWrapper(response))

            if fn.__name__ == func_name:
                uid = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
                with open(f'func_call_{uid}.pkl', 'wb') as file:
                    pickle.dump((args, kwargs, deepcopy(response)), file)
                    
                with open(path, 'a+'):
                    file.write(f'{datetime.timestamp(datetime.now())},{uid},{fn.__module__},{argstr}{kwargstr}{resp}\n')

            if process:
                with open(path, 'r') as file:
                    text = file.read()

                data = []
                for i, line in text.split('\n'):
                    datum = []
                    for val in line.split(','):
                        val.replace(';',',')
                        datum.append(val)
                    data.append(datum)

                df = pd.DataFrame(data, columns=['CALL ID', 'UID','Module', 'Arguments', 'Keyword Arguments', 'Return Value'])
            
            return response
            
        return inner
        
    return outer