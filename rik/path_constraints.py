import glob
import os
import re

# pylint: disable=too-few-public-methods

SUFFIX_SIZE_MAP = {
    'b' : 1,
    'k' : 1024,
    'm' : 1024 * 1024,
    'g' : 1024 * 1024 * 1024,
}

class PathConstraint:
    # pylint: disable=no-self-use

    def __init__(self):
        pass

    def check(self, path):
        raise RuntimeError("Not Implemented")

class FileSizeConstraint(PathConstraint):

    def __init__(self, sign = '==', size = None):
        super().__init__()
        self._sign = sign
        self._parse_size(size)

    def _parse_size(self, size):
        if size is None:
            raise RuntimeError("Must Specify Size")

        if isinstance(size, (int, float)):
            self._size = size
            return

        if not isinstance(size, str):
            raise RuntimeError(
                f"Size must be str, int, or float, not '{size}'"
            )

        suffix = size[-1].lower()

        if suffix in SUFFIX_SIZE_MAP:
            size = int(size[:-1]) * SUFFIX_SIZE_MAP[suffix]
        else:
            raise ValueError(f'Unknown size suffix: {suffix}')

        self._size = size

    def check(self, path):
        # pylint: disable=superfluous-parens
        if not os.path.isfile(path):
            return False

        size = os.path.getsize(path)

        if self._sign == '>':
            return (size > self._size)

        if self._sign == '>=':
            return (size >= self._size)

        if self._sign == '<':
            return (size < self._size)

        if self._sign == '<=':
            return (size <= self._size)

        return (size == self._size)

    @staticmethod
    def from_string(spec):
        # pylint: disable=no-else-return

        if len(spec) < 2:
            raise RuntimeError(f"Failed to parse size spec: '{spec}'")

        prefix = spec[0]

        if prefix in [ '>', '+']:
            if spec[1] == '=':
                return FileSizeConstraint('>=', spec[2:])
            else:
                return FileSizeConstraint('>', spec[1:])

        if prefix in [ '<', '-' ]:
            if spec[1] == '=':
                return FileSizeConstraint('<=', spec[2:])
            else:
                return FileSizeConstraint('<', spec[1:])

        if prefix == '=':
            return FileSizeConstraint('==', spec[1:])

        return FileSizeConstraint(0, spec)

class GlobConstraint(PathConstraint):

    def __init__(self, glob_expr, inverse):
        super().__init__()
        self._glob_re = re.compile(glob.fnmatch.translate(glob_expr))
        self._inverse = inverse

    def check(self, path):
        # pylint: disable=superfluous-parens
        basename = os.path.basename(path)
        return ((self._glob_re.match(basename) is not None) != self._inverse)

