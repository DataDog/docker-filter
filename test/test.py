import unittest
import docker
import re
import time
from multiprocessing import Process


# Main class
class dockerTest(unittest.TestCase):
    def setUp(self):
        self.client = docker.from_env()

    def tearDown(self):
        self.client = None

    @property
    def my_cid(self):
        REGEX_PATTERN = '(.*/)+([a-z0-9]{64})$'
        cgroup_path = '/proc/self/cgroup'
        with open(cgroup_path, 'r') as f:
            for ind in f:
                id_match = re.search(REGEX_PATTERN, ind)
                if id_match:
                    return id_match.group(2)
        self.fail("could not find our container id")

    @property
    def my_inspect(self):
        return self.client.containers.get(self.my_cid)


# These should work
class TestDockerAllow(dockerTest):
    def test_ping(self):
        self.client.ping()

    def test_info(self):
        self.assertIsNotNone(self.client.info())

    def test_list_containers(self):
        containers = self.client.containers.list()
        self.assertTrue(len(containers) >= 2)

        my_cid = self.my_cid
        found = False
        for co in containers:
            if co.id == my_cid:
                found = True
        self.assertTrue(found, "can't find myself, container %s" % my_cid)

    def test_inspect_container(self):
        self.assertIsNotNone(self.my_inspect)

    def test_list_volumes(self):
        self.assertIsNotNone(self.client.volumes.list())

    def test_inspect_volume(self):
        vol_id = None
        for mount in self.my_inspect.attrs.get('Mounts', []):
            if mount.get("Type") == "volume":
                vol_id = mount['Name']
        self.assertIsNotNone(vol_id, "can't find a volume attached to me")
        self.assertIsNotNone(self.client.volumes.get(vol_id))

    def test_list_images(self):
        self.assertIsNotNone(self.client.images.list())

    def test_inspect_images(self):
        img_id = self.my_inspect.attrs['Image']
        self.assertIsNotNone(self.client.images.get(img_id))


# All of these should fail. Not testing every POST request
# as the filter is common, but testing all blacklisted GETs
class TestDocker403(dockerTest):
    def assert403(func):
        def ret_fn(self, *args, **kwargs):
            with self.assertRaisesRegexp(docker.errors.APIError, '403 Client Error: Forbidden'):
                return func(self, *args, **kwargs)
        return ret_fn

    @assert403
    def test_run(self):
        self.client.containers.run('redis', detach=True)

    @assert403
    def test_prune(self):
        self.client.containers.prune()

    @assert403
    def test_container_changes(self):
        self.my_inspect.diff()

    @assert403
    def test_container_export(self):
        self.my_inspect.export()

    @assert403
    def test_container_attach(self):
        self.my_inspect.attach()

    @assert403
    def test_container_attach_ws(self):
        self.my_inspect.attach_socket()

    @assert403
    def test_container_archive(self):
        self.my_inspect.get_archive("/")

    @assert403
    def test_image_search(self):
        self.client.images.search("docker-dd-agent")

    @assert403
    def test_image_export(self):
        client = docker.APIClient()
        client.get_image("redis")

    @assert403
    def test_secrets(self):
        self.client.secrets.list()

    @assert403
    def test_secret_get(self):
        self.client.secrets.get("dummy")


# Testing we don't timeout on the events and logs endpoints
class TestDockerNoTimeout(dockerTest):
    def setUp(self):
        self.client = docker.from_env(timeout=60)

    def consume_generator(self, gen):
        for i in gen:
            continue

    def test_no_timeout(self):
        event_filter = {"id": "invalidContainerIDNoEvents"}  # To make sure we collect no event
        events_consumer = Process(target=self.consume_generator,
                                  args=(self.client.events(filters=event_filter),))
        events_consumer.daemon = True
        events_consumer.start()

        logs_consumer = Process(target=self.consume_generator,
                                args=(self.my_inspect.logs(stream=True, follow=True),))
        logs_consumer.daemon = True
        logs_consumer.start()

        # Make sure we don't EOF for 25 seconds
        for i in range(1, 25):
            time.sleep(1)
            self.assertTrue(events_consumer.is_alive(), msg="events died after %s seconds" % (i))
            self.assertTrue(logs_consumer.is_alive(), msg="logs died after %s seconds" % (i))

        logs_consumer.terminate()
        events_consumer.terminate()


if __name__ == '__main__':
    unittest.main()
