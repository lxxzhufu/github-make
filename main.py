import encodings.idna
import argparse
import paramiko


# 其实命令和脚本实质上是不冲突的啊


# 开始登录执行命令
def freeConfidentiality(ip, username, password, port, commands, sudo_flag, script_args):
    # private_key = paramiko.RSAKey.from_private_key_file('/usr/id_rsa')
    sshClient = paramiko.SSHClient()
    # ssh访问的策略
    policy = paramiko.AutoAddPolicy()
    # 使用密码登录
    sshClient.set_missing_host_key_policy(policy)
    # ssh.connect(ip, port, user, pkey=private_key)
    try:
        sshClient.connect(hostname=ip, port=port, username=username, password=password)
        if sudo_flag:
            stdin, stdout, stderr = sshClient.exec_command(
                f"export function={script_args};{commands}", get_pty=True
            )
            stdin.write(password + "\n")
        else:
            stdin, stdout, stderr = sshClient.exec_command(
                f"export function={script_args};{commands}", get_pty=True
            )
        normal_info = stdout.read().decode()
        errors = stderr.read().decode()
        # 命令太长禁用输出(主要是脚本问题, 没有测试过过长的传递会有什么问题)
        if len(commands) < 100:
            print(f"{ip} commands: ['{commands}'] info:\n{normal_info}", end="")
        else:
            print(f"{ip} info:\n{normal_info}", end="")
    except Exception as e:
        print(f"{ip} error: {e}")
    finally:
        sshClient.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="remoute handle command")

    # 还是给点实用性的选项
    parser.add_argument("-p", "--port", type=str, default="22", help="SSH Port")
    parser.add_argument(
        "-P", "--password", type=str, default="root", help="SSH Password"
    )
    parser.add_argument("-u", "--user", type=str, default="root", help="SSH Username")
    parser.add_argument("-H", "--host", type=str, default="localhost", help="SSH Host")
    parser.add_argument(
        "-c", "--command", type=str, default="hostname", help="SSH Command"
    )
    parser.add_argument("-f", "--function", type=str, default="", help="Script Args")
    parser.add_argument(
        "-key", "--privatekey", type=str, default="/root/.ssh/", help="SSH Private Key"
    )
    args = parser.parse_args()

    # 要判断一下命令里面有没有sudo提权
    if "sudo" in args.command:
        sudo_flag = True
    else:
        sudo_flag = False

    freeConfidentiality(
        ip=args.host,
        port=args.port,
        username=args.user,
        commands=args.command,
        password=args.password,
        sudo_flag=sudo_flag,
        script_args=args.function,
    )
