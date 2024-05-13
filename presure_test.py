from locust import HttpUser, TaskSet, task



class WebsiteUser(HttpUser):
    min_wait = 5000
    max_wait = 9000
    host = 'http://127.0.0.1:80/'


    @task
    def a(self):
        self.client.get("/")