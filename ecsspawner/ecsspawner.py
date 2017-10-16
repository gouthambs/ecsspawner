import boto3
from tornado import gen
from jupyterhub.spawner import Spawner
from traitlets import (
    Dict,
    Unicode,
    List,
    Bool,
    Int,
)



class ECSSpawner(Spawner):
    ecs_client = boto3.client("ecs")
    ec2_client = boto3.client('ec2')
    cluster_name = Unicode("notebook-cluster",
                           help="Name of the cluster setup")
    task_definition = Unicode("ql_notebook_spawner_task:3",
                              help="The task definition in <defn>:<revision> format")
    task_arn = Unicode()
    container_instance_arn = Unicode()

    def load_state(self, state):
        super().load_state(state)
        self.task_arn = state.get('task_arn', '')
        self.container_instance_arn = state.get('container_instance_arn', '')

    def get_state(self):
        state = super().get_state()
        if self.task_arn:
            state['task_arn'] = self.task_arn
        if self.container_instance_arn:
            state['container_instance_arn'] = self.container_instance_arn

        return state

    @gen.coroutine
    def poll(self):
        if self.task_arn:
            res = self.ecs_client.describe_tasks(
                cluster=self.cluster_name,
                tasks = [self.task_arn]
            )
            if res['tasks'][0]['lastStatus'].lower() == 'running':
                return None
            else:
                return 1
        else:
            return 0


    @gen.coroutine
    def start(self):
        client = self.ecs_client
        resp1 = yield client.run_task(cluster=self.cluster_name, taskDefinition=self.task_definition,
                                count=1, startedBy="ecsspawner")
        self.task_arn = resp1['tasks'][0]['containers'][0]['taskArn']
        container_instance_arn = resp1['tasks'][0]['containerInstanceArn']
        resp2 = yield client.describe_tasks(cluster=self.cluster_name, tasks=[self.task_arn])
        host_port = resp2['tasks'][0]['networkBindings']['hostPort']
        resp3 = client.describe_container_instances(cluster=self.cluster_name,
                                                    containerInstances=[container_instance_arn])
        ec2_instance_id = resp2['containerInstances'][0]['ec2InstanceId']

        resp4 = self.ec2_client.describe_instances(InstanceIds=[ec2_instance_id])
        public_ip = resp4['Reservations'][0]['Instances'][0]['PublicIpAddress']
        private_ip = resp4['Reservations'][0]['Instances'][0]['PrivateIpAddress']

        return (public_ip, host_port)

    def stop(self, now=False):
        self.log.info("Stopping task %s" % self.task_arn)
        yield self.ecs_client.stop_task(
            cluster=self.cluster_name,
            task=self.task_arn,
            reason="Shutdown by the hub"
        )
        self.log.info("The requested task has been stopped")
        self.clear_state()
