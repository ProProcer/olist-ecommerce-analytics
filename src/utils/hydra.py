from hydra.utils import instantiate as _instantiate

try:
    from hydra.utils import UNSAFE_ALLOW_ALL_TARGETS
    _TARGET_WHITELIST = {'_target_whitelist_': UNSAFE_ALLOW_ALL_TARGETS}
except ImportError:
    _TARGET_WHITELIST = {}


def instantiate_unsafe(config, *args, **kwargs):
    return _instantiate(config, *args, **_TARGET_WHITELIST, **kwargs)
