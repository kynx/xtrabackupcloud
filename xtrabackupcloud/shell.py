
from logging import DEBUG
import subprocess


class ShellException(Exception):
    pass


def xtrabackup(out_file, logger, log_level=DEBUG, **kwargs):

    args = ['xtrabackup'] + _get_args(**kwargs)
    logger.log(log_level, "Running '{}'".format(" ".join(args)))
    
    try:
        # stdout to file, stderr to logger
        with open(out_file, 'wb+') as f:
            proc = subprocess.Popen(args, stdout=f, stderr=subprocess.PIPE)

            def check_io():
                while True:
                    output = proc.stderr.readline().decode()
                    if output:
                        logger.log(log_level, output.rstrip())
                    else:
                        break

            while proc.poll():
                check_io()

            check_io()
            proc.wait()

    except IOError as e:
        raise ShellException("IO error on {}: {}".format(file, str(e)))
    except OSError as e:
        raise ShellException("Failed to run xtrabackup: {}".format(str(e)))


def partition(device):
    proc = subprocess.Popen(['sfdisk', '-q', device], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # <start>,<size>,<id> - empty size means use entire disk
    stdout, stderr = proc.communicate(input="2048,,83", timeout=10)
    if proc.returncode:
        raise ShellException("Failed to format {}: {}".format(device, stderr))


def mount(device, dir):
    _check_call(['mount', device, dir])


def umount(dir, lazy=True):
    args = ['umount']
    if lazy:
        args.append('-l')
    args.append(dir)

    _check_call(args)


def _check_call(args, stdin=None, stdout=None, env=None):
    try:
        subprocess.check_call(args, stdin, stdout, env)
    except subprocess.CalledProcessError as e:
        raise ShellException(args[0] + " failed: " + str(e))
    except OSError as e:
        raise ShellException("Failed to run shell " + args[0] + ": " + str(e))


def _get_args(**kwargs):
    args = []
    for arg, val in kwargs.iteritems():
        if val is True:
            args.append(_kw2opt(arg))
        elif val:
            args.append(_kw2opt(arg))
            args.append(val)
    return args


def _kw2opt(kw):
    return '--' + kw.replace('_', '-')
