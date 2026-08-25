from omegaconf import OmegaConf

def add(*args):
    for i, val in enumerate(args):
        if i == 0:
            result = val
            continue
        result = result +  val
    return result

def register_custom_resolvers():
    OmegaConf.register_new_resolver('add', add, replace = True)