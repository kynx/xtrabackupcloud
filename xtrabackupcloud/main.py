import argparse
from ConfigParser import ConfigParser
from os import path
from platform import node
import StringIO

from . import backup, restore
from cloud import *

_config_files = ["/etc/xtrabackupcloud/config.cfg", path.expanduser("~/.xtrabackupcloud")]


def main():
    defaults = {
        "block-storage-name": node() + "-xtrabackupcloud",
        "block-storage-size": "100",
        "container": "xtrabackup",
        "datadir": "/var/lib/mysql",
        "delay": "60",
        "log-level": "info",
        "log-file": None,
        "mount-device": "",
        "mount-dir": "/mnt/backup",
        "prefix": node(),
        "provider": "rackspace",
        "retry": "5",
        "temp-block-storage": "no",
        "working-dir": "~/xtrabackup_backupfiles"
    }

    config = ConfigParser(defaults, allow_no_value=True)
    for section in ['xtrabackupcloud', 'xtrabackup', 'mysqld'] :
        config.add_section(section)
    configs = config.read(_config_files)

    parser = argparse.ArgumentParser(description="MySQL backup to cloud provider")
    parser.add_argument(
        "--container",
        default=config.get("xtrabackupcloud", "container"),
        help="Container to store backup in"
    )
    parser.add_argument(
        "--delay",
        default=config.get("xtrabackupcloud", "delay"),
        help="Seconds between re-trying cloud operations"
    )
    parser.add_argument(
        "--extra-config",
        action="append",
        help="Extra configuration file(s) to parse"
    )
    parser.add_argument(
        "--prefix",
        default=config.get("xtrabackupcloud", "prefix"),
        help="Prefix to prepend when storing backup in container"
    )
    parser.add_argument(
        "--provider",
        choices=["rackspaace", "amazon", "google"],
        default=config.get("xtrabackupcloud", "provider"),
        help="Cloud provider"
    )
    parser.add_argument(
        "--retry",
        default=config.get("xtrabackupcloud", "retry"),
        help="Number of times to re-try failed cloud operations"
    )
    parser.add_argument(
        "--working-dir",
        default=config.get("xtrabackupcloud", "working-dir"),
        help="Working directory"
    )

    subparsers = parser.add_subparsers()

    backup_parser = subparsers.add_parser("backup", help="Perform backup")
    backup_parser.add_argument(
        "--block-storage-name",
        type=int,
        default=config.getint("xtrabackupcloud", "block-storage-name"),
        help="Name of block storage"
    )
    backup_parser.add_argument(
        "--block-storage-size",
        type=int,
        default=config.getint("xtrabackupcloud", "block-storage-size"),
        help="Size of block storage in gigabytes"
    )
    backup_parser.add_argument(
        "--incremental",
        action="set_true",
        help="Perform incremental backup"
    )
    backup_parser.add_argument(
        "--log-file",
        default=config.get("xtrabackupcloud", "log-file"),
        help="File to log backups progress"
    )
    backup_parser.add_argument(
        "--log-level",
        default=config.get("xtrabackupcloud", "log-level"),
        help="Log level (ie 'info', 'warn')"
    )
    backup_parser.add_argument(
        "--mount-device",
        default=config.get("xtrabackupcloud", "mount-device"),
        help="Device name to mount block storage on (ie '/dev/xvdb1')"
    )
    backup_parser.add_argument(
        "--temp-block-storage",
        default=config.getboolean("xtrabackupcloud", "temp-block-storage"),
        action="store_true",
        help="Use temporary block storage when creating backup"
    )
    backup_parser.set_defaults(func=backup)

    restore_parser = subparsers.add_parser("restore", help="Restore backup")
    restore_parser.add_argument(
        "--datadir",
        default=config.get("mysqld", "datadir"),
        help="Directory to restore to"
    )
    restore_parser.set_defaults(func=restore)

    args = parser.parse_args()

    for extra_config in args.extra_config :
        config.read(path.expanduser(extra_config))

    args.func(_get_provider(args, config), args)


def parse_checkpoint_file(checkpoint_file):
    parsed = {}
    if path.exists(checkpoint_file):
        config = ConfigParser()
        cp_string = '[default]\n' + open(checkpoint_file).read()
        config.readfp(StringIO.StringIO(cp_string))
        for option in config.options('default'):
            parsed[option] = config.get('default', option)

    return parsed


def get_checkpoint_file(working_dir):
    return path.join(working_dir, 'xtrabackup_checkpoints')


def _get_provider(args, config):
    if args.provider == 'rackspace':
        if not config.has_section('rackspace_cloud'):
            raise Exception("Cannot find 'rackspace_cloud' section in configuration")

        return rackspace.Rackspace(
            args.retry,
            args.delay,
            region=config.get('rackspace_cloud', 'region'),
            username=config.get('rackspace_cloud', 'username'),
            api_key=config.get('rackspace_cloud', 'api_key')
        )
