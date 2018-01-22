
import base
import pyrax


class Rackspace(base.Base):

    def __init__(self, retries, delay, region, username, api_key, use_servicenet=True):
        super(Rackspace, self).__init__(retries, delay)

        pyrax.set_setting("identity_type", "rackspace")
        pyrax.set_setting("use_servicenet", use_servicenet)
        pyrax.set_credentials(username, api_key, region)

    def get_block_storage(self, block_storage_name):
        return self._attempt(self._get_block_storage, block_storage_name)

    def _get_block_storage(self, block_storage_name):
        cbs = pyrax.cloud_blockstorage
        block_storage = cbs.findall(name=block_storage_name)
        if len(block_storage):
            return block_storage[0]

    def create_block_storage(self, server, block_storage_name, block_storage_size):
        if not self.get_block_storage(block_storage_name):
            self._attempt(self._create_block_storage, server, block_storage_name, block_storage_size)

    def _create_block_storage(self, server, block_storage_name, block_storage_size):
        vol = self._get_block_storage(block_storage_name)
        if not vol:
            cbs = pyrax.cloud_blockstorage
            vol = cbs.create(name=block_storage_name, size=block_storage_size)
            pyrax.utils.wait_until(vol, 'status', 'available', attempts=0)

        vol.attach_to_instance(server, mountpoint=mount_device)
        pyrax.utils.wait_until(vol, 'status', 'in-use', attempts=0)

    def delete_block_storage(self, server, block_storage_name):
        self._attempt(self._delete_block_storage, server, block_storage_name)

    def _delete_block_storage(self, block_storage_name):
        block_storage = self._get_block_storage(block_storage_name)
        if block_storage.status != 'available':
            block_storage.detach()
            pyrax.utils.wait_until(vol, 'status', 'available', attempts=0)
        block_storage.delete()

    def container_exists(self, container):
        pass

    def create_container(self, container):
        pass

    def list(self, container, prefix):
        pass

    def upload(self, path, container, name):
        pass

    def download(self):
        pass

