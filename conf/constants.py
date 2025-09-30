VERSION = 'v0.3'
RELEASE_DATE = '2023-Jun-03'
AUTHOR = 'Randy E. Oyarzabal'
GIT_REPO = 'https://github.com/randyoyarzabal/stocks'


def banner(tool):
    return '{} ver. {} ({})'.format(tool.split('.')[0].upper(), VERSION, RELEASE_DATE)
