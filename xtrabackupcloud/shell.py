
import subprocess
import tempfile

libexec_dir = '/usr/local/libexec'


class ShellException(Exception):
    pass


def xtrabackup(file, verbose=0, **kwargs):

    if verbose:
        out = None
    else:
        out = tempfile.TemporaryFile()

    args = ['xtrabackup'] + _get_args(**kwargs)

    try:
        with open(file, 'wb+') as f:
            subprocess.check_call(args, stdout=f, stderr=out)
    except IOError as e:
        raise ShellException("IO error on " + file + ": " + str(e))
    except subprocess.CalledProcessError as e:
        raise ShellException("xtrabackup failed: " + str(e))
    except OSError as e:
        raise ShellException("Failed to run xtrabackup: " + str(e))


def mount(dir):
    _check_call(['mount', dir])


def umount(dir, lazy=True):
    args = ['umount']
    if lazy:
        args.append('-l')
    args.append(dir)

    _check_call(args)


def prepare_backup_device(device):
    _check_call(['sudo', libexec_dir + '/prepare-backup-device.sh'], env={'XBC_BACKUP_DEVICE': device})


def set_mysql_perms(datadir):
    _check_call(['sudo', libexec_dir + '/mysql-perms.sh'], env={'XBC_DATA_DIR': datadir})


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
