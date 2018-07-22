import docker
import threading
import timeit
import socket
import json

cli = docker.from_env()
instances = cli.containers.list()

mainsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
connection = []

class Stats(threading.Thread):
    def __init__(self, container):
        threading.Thread.__init__(self)
        self.container = container
        self.name = container.name
        self.stats = container.stats()
        self.pre_stats = None
        self.pre_time = None

    def run(self):
        while 1:
	    if self.pre_stats:
                cur_stats = eval(self.stats.next())
                cpu_usage = self.cpu_monitor(self.pre_stats['cpu_stats'], cur_stats['cpu_stats'])
                msg = { 'cpu_usage': str(cpu_usage), 'name': self.name }
	        for i, conn in enumerate(connection):
                    try:
                        conn[0].send(json.dumps(msg))
                    except:
                        print('exception')
                        del connection[i]
            self.pre_stats = eval(self.stats.next())
                
    def cpu_monitor(self, pre_cpu, cur_cpu):
        cpu_delta = cur_cpu['cpu_usage']['total_usage'] - pre_cpu['cpu_usage']['total_usage']
        system_delta = cur_cpu['system_cpu_usage'] - pre_cpu['system_cpu_usage']
        if system_delta > 0:
            return float(cpu_delta) / float(system_delta) * 100.0 * cur_cpu['online_cpus']
        return 0.0
                
class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        mainsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        mainsocket.bind(('', 12345))
        mainsocket.listen(10)
        print('socket listening')
        while 1:
            conn, addr = mainsocket.accept()
            connection.append((conn, addr))

def getInstancesStatus():
    
    threads = [Stats(i) for i in instances]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


server_thread = Server()
server_thread.start()
getInstancesStatus()
server_thread.join()
