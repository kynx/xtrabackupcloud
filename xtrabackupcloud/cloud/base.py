from time import sleep


class Base(object):
    """
    Base class for interacting with cloud providers
    """
    def __init__(self, retries, delay):
        self.retries = retries
        self.delay = delay
        self.fails = 0

    def get_block_storage(self, block_storage_name):
        raise NotImplementedError

    def create_block_storage(self, server, block_storage_name, block_storage_size):
        raise NotImplementedError

    def delete_block_storage(self, block_storage_name):
        raise NotImplementedError

    def container_exists(self, container):
        raise NotImplementedError

    def create_container(self, container):
        raise NotImplementedError

    def list(self, container, prefix):
        raise NotImplementedError

    def upload(self, path, container, name):
        raise NotImplementedError

    def download(self, container, name, path):
        raise NotImplementedError

    def delete(self, container, name):
        raise NotImplementedError

    def get_num_fails(self):
        """Returns total number of failures communicating with cloud provider"""
        return self.fails

    def _attempt(self, cmd, *args):
        tries = 0;
        e = None
        while tries <= self.retries:
            try:
                cmd(*args)
                tries = tries + 1
            except Exception as e:
                sleep(self.delay)
        self.fails = self.fails + tries
        if tries > self.retries:
            raise e
