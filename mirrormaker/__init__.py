from importlib.metadata import version

try:
    __version__ = version('gitlab-mirror-maker')
except:
    __version__ = '0.0.0'
