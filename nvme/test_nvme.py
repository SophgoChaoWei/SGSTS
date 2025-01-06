import logging
import shutil
import subprocess
import os
import datetime

class FioProcess:
    def __init__(   self,
                    direct = True,
                    iodepth = 64,
                    bs = 64 * 1024 * 1024,
                    size = 64 * 1024 * 1024,
                    name = 'nvme-stability',
                    wd = ''):
        self.direct = direct
        self.iodepth = iodepth
        self.bs = bs
        self.size = size
        self.name = name
        self.data = '{}.data'.format(name)
        self.log = '{}.log'.format(name)
        self.wd = wd

        cmd = ['fio']
        cmd.append('-direct={}'.format(1 if direct else 0))
        cmd.append('-iodepth={}'.format(iodepth))
        cmd.append('-rw=write')
        cmd.append('-ioengine=psync')
        cmd.append('-bs={}'.format(bs))
        cmd.append('-size={}'.format(size))
        cmd.append('-numjobs=1')
        cmd.append('-group_reporting')
        cmd.append('-name={}'.format(name))
        cmd.append('-verify=crc32c')
        cmd.append('-do_verify=1')
        cmd.append('-verify_dump=1')
        cmd.append('--aux-path={}'.format(wd))
        cmd.append('--filename={}/{}'.format(wd, self.data))
        cmd.append('--output={}/{}'.format(wd, self.log))

        self.cmd = cmd

        self.stdout = ''
        self.stderr = ''
        self.returncode = None

    def __str__(self):
        return ' '.join(str(opt) for opt in self.cmd)

    def start(self):
        self.process = subprocess.Popen(self.cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    def poll(self):
        return self.process.poll()

    def wait(self):
        self.returncode = self.process.wait()
        self.stdout = self.process.stdout.read()
        self.stderr = self.process.stderr.read()
        return self.returncode;
        
    

def test():
    parallel_threads = 16
    test_size = 1 * 1024 * 1024 * 1024

    fio = shutil.which('fio')
    if (not fio):
        logging.warning('fio not found in system, please install it first')
        assert False

    nvme_test_path = os.environ.get('SGSTS_NVME_PATH')

    if (not nvme_test_path):
        logging.warning('Environment SGSTS_NVME_PATH should be set first (export SGSTS_NVME_PATH=path/to/data)')
        assert False

    if (not os.path.exists(nvme_test_path)):
        logging.warning('{} doesn\'t exist, please create it first'.format(nvme_test_path))
        assert False

    time = datetime.datetime.now()
    time_str = '{}-{}-{}-{:02}{:02}{:02}'.format(time.year, time.month, time.day,
                                                    time.hour, time.minute, time.second)
    fio_processes = []
    for i in range(parallel_threads):
        name = '{}-{}'.format(time_str, i)
        p = FioProcess(wd = nvme_test_path, name = name, size = test_size)
        fio_processes.append(p)

    for i in fio_processes:
        i.start()
        logging.warning(p)

    result = True;

    for i in fio_processes:
        i.wait()
        logging.warning(i.stdout)
        if (i.returncode != 0):
            logging.warning('{} Failed with error {}'.format(i, i.returncode))
            result = False

    assert result
