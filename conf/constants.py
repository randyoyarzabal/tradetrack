VERSION = 'v2.0'
RELEASE_DATE = '2025-Oct-15'
AUTHOR = 'Randy E. Oyarzabal'
GIT_REPO = 'https://gitlab.homelab.io/techno/tradetrack'


def banner(tool):
    return '{} ver. {} ({})'.format(tool.split('.')[0].upper(), VERSION, RELEASE_DATE)
