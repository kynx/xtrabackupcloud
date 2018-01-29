
from datetime import date, datetime
from os import mkdir, path, unlink
import re

from . import shell
from .main import get_checkpoint_file, parse_checkpoint_file


def backup(provider,
           logger,
           incremental=False,
           temp_block_storage=False,
           block_storage_name="xtrabackupcloud",
           block_storage_size=100,
           mount_device="",
           working_dir="",
           container="xtrabackup",
           prefix=None,
           **kwargs
           ):
    working_dir = path.expanduser(working_dir)
    if not path.isdir(working_dir):
        mkdir(working_dir)

    kwargs.update({
        "backup": True,
        "extra_lsndir": working_dir,
        "stream": "xbstream"
    })

    if mount_device:
        out_dir = path.join(working_dir, 'out')
    else:
        out_dir = working_dir

    if mount_device and not path.ismount(out_dir):
        block_device = re.sub("\d+$", "", mount_device)
        if temp_block_storage and not path.exists(block_device):
            logger.info("Creating {}G block storage '{}'".format(block_storage_size, block_storage_name))
            provider.create_block_storage(block_storage_name, block_storage_size, block_device)
        if not path.exists(mount_device):
            logger.info("Partitioning block device '{}'".format(block_device))
            shell.partition(block_device)
        logger.info("Mounting '{}' on '{}'".format(mount_device, out_dir))
        shell.mount(mount_device, out_dir)

    lsn = base_date = False
    checkpoint_file = get_checkpoint_file(working_dir)
    if incremental:
        checkpoints = parse_checkpoint_file(checkpoint_file)
        if len(checkpoints):
            lsn = checkpoints['to_lsn']
            base_date = checkpoints['base_date']

    if not lsn or not base_date:
        base_date = date.today().strftime('%Y-%m-%d')
        if incremental:
            logger.warn("Couldn't get lsn and/or base_date. Performing full backup.")
    else:
        kwargs['incremental-lsn'] = lsn

    filename = datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '.xbcrypt'
    filepath = path.join(out_dir, filename)

    logger.info("Backing up to '{}'".format(filepath))
    shell.xtrabackup(filepath, logger, **kwargs)

    upload = "/".join(filter(None, [prefix, base_date, filename]))
    latest = "/".join(filter(None, [prefix, "latest"]))

    logger.info("Uploading '{}' to '{}'".format(filepath, upload))
    provider.upload(filepath, container, upload)

    logger.info("Storing base_date to '{}'", latest)
    provider.store(base_date, container, latest)

    if path.exists(checkpoint_file):
        with open(checkpoint_file, "a") as f:
            f.write("base_date = {}".format(base_date))

    unlink(filepath)
    if mount_device and path.ismount(out_dir):
        logger.info("Unmounting {}".format(out_dir))
        shell.umount(out_dir)
    if temp_block_storage:
        logger.info("Deleting block storage '{}'".format(block_storage_name))
        provider.delete_block_storage(block_storage_name)

    logger.info("Backup complete")
