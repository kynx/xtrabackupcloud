
import ConfigParser
from datetime import date
import os
import shutil
import StringIO
from . import shell


def backup(provider,
        logger,
        temp_block_storage=False,
        block_storage_name="xtrabackupcloud",
        block_storage_size=100,
        compact=True,
        compress_threads=4,
        encrypt="AES256",
        encrypt_key_file="/etc/xtrabackupcloud/key",
        encrypt_threads=4,
        full=True,
        log="/var/log/xtrabackupcloud.log",
        mount_device="",
        prefix="backup",
        slave_info=True,
        verbose=0,
        working_dir=""
):
    if temp_block_storage:
        provider.create_block_storage(block_storage_name, block_storage_size)

    working_dir = os.path.expanduser(working_dir)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir, 0750)

    if mount_device:
        _mount_storage(mount_device, os.path.join(working_dir, 'mnt'))

    base_date = _get_base_date(working_dir) if full or None
    lsn = _get_lsn(working_dir) if full or None

    # can only do an incremental backup if we've previously stored the base_date and lsn
    incremental = base_date and lsn
    if not incremental:
        base_date = date.today().strftime('%Y-%m-%d')


def _mount_storage(mount_device, mount_dir):
    # already mounted?
    if path.ismount(mount_dir):
        return

    shell.prepare_backup_device(mount_device)
    shell.mount(mount_dir)


def _get_lsn(working_dir):
    checkpoint_file = working_dir + '/xtrabackup_checkpoints'
    if os.path.exists(checkpoint_file):
        shutil.copy(checkpoint_file, checkpoint_file + '.bak')
        cp_string = '[default]\n' + open(checkpoint_file).read()
        checkpoints = ConfigParser.SafeConfigParser()
        checkpoints.readfp(StringIO.StringIO(cp_string))
        return checkpoints.get('default', 'to_lsn')


def _get_base_date(working_dir):
    file = working_dir + '/base_date'
    if os.path.exists(file):
        with open(file, 'r') as base:
            return base.readline()