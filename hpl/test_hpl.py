import logging
import shutil
import subprocess
import os
import datetime
import time

def test(tmp_path):
    parallel_threads = 64

    if (not shutil.which('xhpl')):
        logging.warning('xhpl not found in system, please install it first')
        assert False

    if (not shutil.which('mpirun')):
        logging.warning('mpirun not found in system, please install it first')
        assert False


    test_case_path = os.environ.get('PYTEST_CURRENT_TEST')

    test_case_path = test_case_path[:test_case_path.find(':')]

    test_case_path = os.path.dirname(os.path.abspath(test_case_path))

    shutil.copy('{}/HPL.dat'.format(test_case_path), tmp_path)

    cmd = ['mpirun', '-np', '{}'.format(parallel_threads), 'xhpl']

    now = datetime.datetime.now()
    time_str = '{}-{}-{}-{:02}{:02}{:02}'.format(now.year, now.month, now.day,
                                                 now.hour, now.minute, now.second)

    stdout_file_name = '{}/{}.stdout.log'.format(tmp_path, time_str)
    stderr_file_name = '{}/{}.stderr.log'.format(tmp_path, time_str)

    stdout = open(stdout_file_name, 'w')
    stderr = open(stderr_file_name, 'w')

    process = subprocess.Popen(cmd, stdout = stdout, stderr = stderr, cwd = tmp_path)

    while (True):
        returncode = process.poll()
        if (returncode == None):
            stdout.flush()
            stderr.flush()
            time.sleep(1)
        else:
            break;

    stdout.close()
    stderr.close()

    if (returncode != 0):
        logging.warning('xhpl failed with error code {}'.format(returncode))
        logging.warning('Command: {}'.format(' '.join(str(opt) for opt in cmd)))
        logging.warning('Working directory: {}'.format(tmp_path))

    assert returncode == 0
