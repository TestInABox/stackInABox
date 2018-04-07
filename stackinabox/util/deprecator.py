import functools
import warnings


class DeprecatedInterface(object):

    def __init__(self, old_fn, new_fn):
        self.old_fn = old_fn
        self.new_fn = new_fn

    def __call__(self, fn, *args, **kwargs):

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            warnings.warn(
                '"{old_fn}" deprecated in favor of "{new_fn}" for API '
                'consistency, please update'.format(
                    old_fn=self.old_fn,
                    new_fn=self.new_fn
                ),
                DeprecationWarning
            )
            return fn(*args, **kwargs)

        return wrapper
