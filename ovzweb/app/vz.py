import paramiko, json, os


def command(host, command, user='root', json_data=False, keyfile=None):
    home = os.environ.get('HOME')
    if keyfile is None:
        for filename in [home + '/.ssh/cugnet', home + '/.ssh/id_rsa', home + '/.ssh/id_dsa']:
            if os.path.exists(filename) and keyfile == None:
                keyfile = filename
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, key_filename=keyfile)
    stdin, stdout, strerr = ssh.exec_command(command)
    if json_data:
        output = json.load(stdout)
    else:
        output = stdout.readlines()
    ssh.close()
    return output


def list(host, ctid='', **opts):
    cmd = 'vzlist %s %s --json' % (ctid, 
        ' '.join(['--%s %s' % (opt, opts[opt]) for opt in opts]))
    return command(host, cmd, json_data=True)


def ctl(host, ctid, action, **opts):
    cmd = 'vzctl %s %s %s' % (action, ctid, 
        ' '.join(['--%s %s' % (opt, opts[opt]) for opt in opts]))
    return command(host, cmd)