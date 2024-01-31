import encodings.idna
import argparse
import paramiko
import logging
import datetime
import json

# 存在的问题 命令和脚本识别问题


formater = logging.Formatter(
    # "%(asctime)s -[line:%(lineno)d] - %(levelname)s: %(message)s"
    "%(asctime)s - %(levelname)s: %(message)s"
)
# formater = logging.Formatter('%(asctime)s-%(levelname)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)
logging.getLogger("paramiko").setLevel(logging.WARNING)


streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.INFO)
streamHandler.setFormatter(formater)
logger.addHandler(streamHandler)


class HandlerCommand:
    # args参数存在只能和脚本参数存在
    def __init__(self, username, password, port):
        self.username = username
        self.password = password
        self.port = port
        self.result_json = {}
        # 创建SSH客户端
        self.sshClient = paramiko.SSHClient()

    def now_time(self):
        return datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    # 是否执行脚本看是否有脚本参数
    def run(self, host=None, commands=None, scriptPath=None, scriptArgs=None):
        self.host = host
        self.result_json[self.host] = {
            "StartDate": self.now_time(),
        }
        # 自动添加主机到已知主机列表
        try:
            self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.sshClient.connect(
                hostname=host,
                port=self.port,
                username=self.username,
                password=self.password,
            )
            # self.host = host
            self.result_json[self.host]["ConnectMessage"] = f"successed: {self.host}"
            self.result_json[self.host][
                "AuthMessage"
            ] = f"sucessed: {self.username}@{host}"
            logging.info(f"{host} Authentication Successful and Start handle commands")
        except paramiko.AuthenticationException as authen_err:
            # 认证失败
            self.result_json[self.host]["AuthMessage"] = f"failed: {authen_err}"
            self.result_json[self.host]["ResultDate"] = self.now_time()
            logging.error(
                f"Using {self.password} password and {host} Authentication Failed: {authen_err}"
            )
            # result = self.resutl_format(result=self.result_json)
            # print(f"{result},")
            # logging.error(f"{self.host} Tasks Result: \n{result}\n")
            self.sshClient.close()
            exit()
        except paramiko.ssh_exception.NoValidConnectionsError as conn_err:
            # 连接失败
            self.result_json[self.host]["ConnectMessage"] = f"failed {conn_err}"
            self.result_json[self.host]["ResultDate"] = self.now_time()
            logging.error(f"{host} Connection Failed: {conn_err}")
            result = self.resutl_format(result=self.result_json)
            logging.error(f"{self.host} Tasks Result: \n{result}\n")
            self.sshClient.close()
            exit()
        # 连接SSH服务
        try:
            # 单命令执行
            if commands is not None:
                stdin, stdout, stderr = self.sshClient.exec_command(
                    f"{commands}", get_pty=True
                )
                self.result_json[self.host]["Commands"] = f"{commands}"
            else:
                # 获取脚本内容
                script = self.getCommand(scriptPath)
                stdin, stdout, stderr = self.sshClient.exec_command(
                    # 存在参数会注入到环境变量中
                    f"{scriptArgs};{script}",
                    get_pty=True,
                )
                self.result_json[self.host]["Commands"] = f"{scriptArgs};{scriptPath}"
            # 捕捉输出
            normal_info = stdout.read().decode()
            errors = stderr.read().decode()
            self.handle_result(normal_info, errors)
        finally:
            self.sshClient.close()

    def handle_result(self, normal_info, errors):
        if len(errors) != 0:
            #  存在错误字段
            self.result_json[self.host]["ErrorMessage"] = f"Error: {errors.strip()}"
            self.result_json[self.host]["ResultDate"] = self.now_time()
            logging.error(f"{host} Tasks Error: {errors.strip()}\n")
        else:
            # 回显命令执行结果
            self.result_json[self.host]["ResultMessage"] = normal_info
            # 回显参数优化
            self.result_json[self.host]["ResultDate"] = self.now_time()
            # 生成json数据
            result = self.resutl_format(result=self.result_json)
            logging.info(
                f"{self.host} Tasks Finished commands=[{self.result_json[self.host]['Commands']}]\n{normal_info}"
            )

    def resutl_format(self, result):
        js = json.dumps(result, sort_keys=False, indent=4, separators=(", ", ": "))
        return js

    def getCommand(self, fileHost):
        try:
            with open(f"{fileHost}") as sh:
                command = sh.read()
                sh.close()
                return command
        except Exception as e:
            logging.error(e)
