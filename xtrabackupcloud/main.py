import argparse
from ConfigParser import ConfigParser
from os import path
from platform import node

from . import backup, restore
from cloud import *

_config_files = ["/etc/xtrabackupcloud/config.cfg", path.expanduser("~/.xtrabackupcloud")]


def main():
    defaults = {
        "block-storage-name": node() + "-xtrabackupcloud",
        "block-storage-size": "100",
        "compact": "yes",
        "compress-threads": "4",
        "container": "xtrabackup",
        "datadir": "/var/lib/mysql",
        "delay": "60",
        "encrypt": "AES256",
        "encrypt-key-file": "/etc/xtrabackupcloud/key",
        "encrypt-threads": "4",
        "full": "yes",
        "log": "/var/log/xtrabackupcloud.log",
        "mount-device": "",
        "mount-dir": "/mnt/backup",
        "prefix": node(),
        "provider": "rackspace",
        "retry": "5",
        "server-name": node(),
        "slave-info": "yes",
        "temp-block-storage": "yes",
        "working-dir": path.expanduser("~/xtrabackup_backupfiles")
    }

    config = ConfigParser(defaults, allow_no_value=True)
    for section in ['xtrabackupcloud', 'xtrabackup', 'mysqld'] :
        config.add_section(section)
    configs = config.read(_config_files)

    parser = argparse.ArgumentParser(description="MySQL backup to cloud provider")
    parser.add_argument(
        "--compact",
        action="store_true",
        default=config.getboolean("xtrabackup", "compact"),
        help="Remove / rebuild secondary indexes"
    )
    parser.add_argument(
        "--compress-threads",
        type=int,
        default=config.getint("xtrabackup", "compress-threads"),
        help="Number of threads to use when compressing"
    )
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
        "--encrypt",
        choices=["AES128", "AES192", "AES256"],
        default=config.get("xtrabackup", "encrypt"),
        help="Encryption algorithm"
    )
    parser.add_argument(
        "--encrypt-key-file",
        default=config.get("xtrabackup", "encrypt-key-file"),
        help="Encryption key"
    )
    parser.add_argument(
        "--encrypt-threads",
        type=int,
        default=config.getint("xtrabackup", "encrypt-threads"),
        help="Number of threads to use when encrypting"
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
        "-v",
        action="count",
        help="Be verbose (use -vvv to see output from xtrabackup)"
    )
    parser.add_argument(
        "--working-dir",
        default=config.get("xtrabackupcloud", "working-dir"),
        help="Working directory"
    )

    subparsers = parser.add_subparsers()

    backup_parser = subparsers.add_parser("backup", help="Perform backup")
    backup_parser.add_argument(
        "--block-storage-size",
        type=int,
        default=config.getint("xtrabackupcloud", "block-storage-size"),
        help="Size of block storage in gigabytes"
    )
    backup_parser.add_argument(
        "--full",
        action="store_true",
        default=True,
        help="Perform full backup"
    )
    backup_parser.add_argument(
        "--log",
        default=config.get("xtrabackupcloud", "log"),
        help="File to log backups progress"
    )
    backup_parser.add_argument(
        "--mount-device",
        default=config.get("xtrabackupcloud", "mount-device"),
        help="Device name to mount block storage on (ie '/dev/xvdb')"
    )
    backup_parser.add_argument(
        "--server-name",
        default=config.get("xtrabackupcloud", "server-name"),
        help="Server name"
    )
    backup_parser.add_argument(
        "--slave-info",
        action="store_true",
        default=config.getboolean("xtrabackup", "slave-info")
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
