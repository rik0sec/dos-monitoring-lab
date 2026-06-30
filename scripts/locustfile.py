from locust import HttpUser, task, between, constant


class NormalUser(HttpUser):
    host = "http://10.203.226.87:5004"
    weight = 2
    wait_time = between(1, 3)

    @task
    def browse(self):
        self.client.get("/")


class AttackUser(HttpUser):
    host = "http://10.203.226.87:5004"
    weight = 8
    wait_time = constant(0)

    @task(20)
    def flood_fast(self):
        self.client.get("/fast")

    @task(1)
    def flood_heavy(self):
        self.client.get("/heavy?delay=0.1&factor=1")