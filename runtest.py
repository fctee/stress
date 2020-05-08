import random
import paramiko
import traceback


def filetransfer(func):
    def wrapper(self, *args):
        sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
        try:
            func(self, *args)
        except:
            traceback.print_exc()
        sftp.close()
    return wrapper


class CommandIssue:

    """
    paramiko传送指令到远程服务器
    """

    def __init__(self, ip):
        self.ip = ip
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        """连接"""
        self.ssh.connect(hostname=self.ip, port=22, username="root", password="Abc123456789!")

    def close(self):
        """断开"""
        self.ssh.close()

    def execute(self, cmds):
        """执行指令"""
        stdin, stdout, stderr = self.ssh.exec_command(cmds)
        stdout = stdout.readlines()
        stdout = "         ".join(stdout) if stdout else ""
        stderr = stderr.readlines()
        stderr = "         ".join(stderr) if stderr else ""
        print("""
---------------------------------
command: {}
 stdout: {}
 stderr: {}
""".format(cmds, stdout, stderr))

    @filetransfer
    def put(self, source, target):
        sftp.put(source, target)

    @filetransfer
    def get(self, source, target):
        sftp.get(source, target)




if __name__ == '__main__':
    yunips = [
        "121.37.191.34",
        "121.37.164.177",
        "121.37.191.119",
        "121.37.160.63",
        "121.37.181.137"
    ]
    tester = "luzhiqi"

    for index, ip in enumerate(yunips):
        ssh = CommandIssue(ip)
        ssh.connect()
        # ssh.execute("docker kill $(docker ps -q)")docker
        # ssh.execute("cd /home/stress && mv log /home/trash/log%s && mkdir log" % random.randint(0, 9999))
        # first = index * 10
        # last = (index + 1) * 10
        # for i, v in enumerate(range(first, last)):
        #     if v != 49:
        #         ssh.execute(
        #             "docker run -it -d -v/home/stress:/home/stress"
        #             " --cpuset-cpus='{}' stress{}:v0 sh -c "
        #             "'python3 auto_test.py --range {} --tester {}'".format(i, v, v, tester))
        ssh.close()