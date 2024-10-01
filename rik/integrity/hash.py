import hashlib
import os

from ..consts   import RESULT_OK, RESULT_MISMATCH, RESULT_ERROR
from .integrity import Integrity

SUPPORTED_HASHES = [
    'md5', 'sha1', 'sha256', 'sha512'
]

HASH_STORAGE_PREFIX = '.rik_'
HASH_STORAGE_NAMES  = [
    HASH_STORAGE_PREFIX + x for x in SUPPORTED_HASHES
]

HASH_CHUNK_SIZE = 4096
HASH_SEPARATOR  = '  '
ENCODING = 'utf-8'

def escape_path(path):
    if path.find('\n') > 0:
        path = path.replace('\n', '\\n')
        return f'\\"{path}"'
    else:
        return f'"{path}"'

def unescape_path(path):
    if path.startswith('\\"'):
        return path[2:-1].replace('\\n', '\n')

    return path[1:-1]

class HashIntegrity(Integrity):

    def __init__(
        self,
        hash_name  = None,
        writable   = False,
        recalc     = False,
        verbose    = False,
        chunk_size = HASH_CHUNK_SIZE,
    ):
        # pylint: disable=too-many-arguments
        self._hash_name  = hash_name.lower()
        self._chunk_size = chunk_size

        if self._hash_name not in SUPPORTED_HASHES:
            raise ValueError(f"Unknown hash: '{self._hash_name}'")

        super().__init__(
            HASH_STORAGE_PREFIX + self._hash_name, writable, recalc, verbose
        )

    def _load(self):
        if not os.path.isfile(self._storage_path):
            return

        with open(self._storage_path, 'rt', encoding = ENCODING) as f:
            for line in f.readlines():
                line   = line.rstrip('\n')
                tokens = line.split('  ', 1)

                if len(tokens) != 2:
                    raise RuntimeError(
                        f"Failed to parse hash string: '{line}'"
                    )

                digest    = tokens[0]
                file_name = unescape_path(tokens[1])

                self._integrity_dict[file_name] = digest

    @staticmethod
    def _calc_hash(file_path, hash_name, chunk_size):
        m = hashlib.new(hash_name)

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda f=f,s=chunk_size : f.read(s), b''):
                m.update(chunk)

        return m.hexdigest()

    def _calculate(self, file_name):
        file_path = self._get_file_path(file_name)
        digest    = HashIntegrity._calc_hash(
            file_path, self._hash_name, self._chunk_size
        )

        return RESULT_OK, digest

    def _verify(self, file_name):
        file_path = self._get_file_path(file_name)
        digest    = HashIntegrity._calc_hash(
            file_path, self._hash_name, self._chunk_size
        )

        # pylint: disable=no-else-return
        if digest == self._integrity_dict[file_name]:
            return RESULT_OK
        else:
            return RESULT_MISMATCH

    def _delete(self, file_name):
        # pylint: disable=no-else-return
        if file_name in self._integrity_dict:
            return RESULT_OK
        else:
            return RESULT_ERROR

    def _save(self):
        files = list(self._integrity_dict.keys())
        files.sort()

        if not files:
            if os.path.isfile(self._storage_path):
                os.remove(self._storage_path)
            return

        with open(self._storage_path, 'wt', encoding = ENCODING) as f:
            for file_name in files:
                digest = self._integrity_dict[file_name]
                fname  = escape_path(file_name)

                f.write(f"{digest}{HASH_SEPARATOR}{fname}\n")

