# Copyright (c) 2009-2012, Andrew McNabb
# Copyright (c) 2003-2008, Brent N. Chun

import fcntl
import string
import sys

HOST_FORMAT = 'Host format is [user[:passwd]@]host[:port] [user]'


def read_host_files(paths, default_user=None, default_port=None):
    """Reads the given host files.

    Returns a list of (host, port, user) triples.
    """
    hosts = []
    if paths:
        for path in paths:
            hosts.extend(read_host_file(path, default_user=default_user))
    return hosts


def read_host_file(path, default_user=None, default_port=None):
    """Reads the given host file.

    Lines are of the form: host[:port] [login].
    Returns a list of (host, port, user) triples.
    """
    lines = []
    f = open(path)
    for line in f:
        lines.append(line.strip())
    f.close()

    hosts = []
    for line in lines:
        # Skip blank lines or lines starting with #
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        host, port, user, passwd = parse_host_entry(line, default_user, default_port)
        if host:
            hosts.append((host, port, user, passwd))
    return hosts


# TODO: deprecate the second host field and standardize on the
# [user@]host[:port] format.
def parse_host_entry(line, default_user, default_port):
    """Parses a single host entry.

    This may take either the of the form [user@]host[:port] or
    host[:port][ user].

    Returns a (host, port, user) triple.
    """
    fields = line.split(":SEP:")
    if len(fields) != 4:
        sys.stderr.write('Bad line1: "%s". Format should be'
                ' user:SEP:passwd:SEP:host:SEP:port\n' % line)
        return None, None, None
    host_field = fields[0]
    host_field = line
    host, port, user, passwd = parse_host(host_field, default_port=default_port)
    #print( "jkdebug: host %s, port %s, user %s, passwd %s\n" % ( host, port, user, passwd ) )
    if len(fields) == 2:
        if user is None:
            user = fields[1]
        else:
            sys.stderr.write('User specified twice in line: "%s"\n' % line)
            return None, None, None
    if user is None:
        user = default_user
    return host, port, user, passwd


def parse_host_string(host_string, default_user=None, default_port=None):
    """Parses a whitespace-delimited string of "[user@]host[:port]" entries.

    Returns a list of (host, port, user) triples.
    """
    hosts = []
    entries = host_string.split()
    for entry in entries:
        hosts.append(parse_host(entry, default_user, default_port))
    return hosts


def parse_host(host, default_user=None, default_port=None):
    """Parses host entries of the form "[user[:passwd]@]host[:port]".

    Returns a (host, port, user) triple.
    """
    # TODO: when we stop supporting Python 2.4, switch to using str.partition.
    user = default_user
    port = default_port
    if ':SEP:' in host:
        user, host = host.split(':SEP:', 1)
    if ':SEP:' in host:
        host, port = host.rsplit(':SEP:', 1)
    passwd = None
    if ":SEP:" in host:
        passwd, host = host.split(':SEP:')
    passwd = passwd.replace( ":SPACE:", " " )
    return (host, port, user, passwd)


def set_cloexec(filelike):
    """Sets the underlying filedescriptor to automatically close on exec.

    If set_cloexec is called for all open files, then subprocess.Popen does
    not require the close_fds option.
    """
    fcntl.fcntl(filelike.fileno(), fcntl.FD_CLOEXEC, 1)
