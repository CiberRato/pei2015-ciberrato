servers = {
    'development': [
        ''
    ],
    'production': [
        'ciber'
    ]
}


def get_server_type():
    from socket import gethostname

    server_name = gethostname()
    for server_type, names in servers.items():
        if server_name in names:
            return server_type

    return 'development'


exec ("from %s import *" % get_server_type())
