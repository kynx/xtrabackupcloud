
from datetime import date
from os import path, pathsep
import re


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
        full_date_formatter="%d",
        full_date_match="01",
        log="/var/log/xtrabackupcloud.log",
        mount_device="",
        prefix="backup",
        slave_info=True,
        verbose=0,
        working_dir=""
):
    working_dir = path.expanduser(working_dir)

    if temp_block_storage:
        provider.create_block_storage(block_storage_name, block_storage_size)

    if mount_device:
        _mount_storage(mount_device, path.join(pathsep, [working_dir, 'mnt']))

    today = date.today()
    if _date_is_fullbackup(today, full_date_formatter, full_date_match):
        pass


def _mount_storage(mount_device, mount_dir):
    if not path.ismount(mount_dir):
        pass


def _date_is_fullbackup(date, full_date_formatter, full_date_match):

    return re.compile(full_date_match).match(date.strftime(full_date_formatter))


