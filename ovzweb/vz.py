import paramiko, base64, json

def _command(host, ssh_key, command, user='root'):
	with open(ssh_key) as keyfile:
		key = paramiko.RSAKey(data=base64.decodestring(keyfile.read()))

	client = paramiko.SSHClient()
	client.get_host_keys().add(host, 'ssh-rsa', key)
	client.connect(host, username=user)
	stdin, stdout, stderr = client.exec_command(command)
	client.close()
	return stdout, strerr


def ctl(host, ctid, action, **opts):
    cmd = 'vzctl %s %s %s' % (action, ctid, ' '.join([
        '--%s %s' % (opt, opts[opt] for opt in opts)
    ]))
    return _command(host, cmd)