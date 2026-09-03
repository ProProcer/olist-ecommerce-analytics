from omegaconf import OmegaConf

def add(*args):
    for i, val in enumerate(args):
        if i == 0:
            result = val
            continue
        result = result +  val
    return result

def register_custom_resolvers():
    register = getattr(OmegaConf, 'register_new_resolver', OmegaConf.register_resolver)
    try:
        register('add', add, replace = True)
    except TypeError:
        register('add', add)