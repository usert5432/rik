import os

from ..consts import RESULT_OK, RESULT_SKIP, RESULT_NEW, RESULT_ERROR

class Integrity:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=no-self-use

    def __init__(self, storage_name, writable, recalc, verbose):
        self._root           = None
        self._storage_name   = storage_name
        self._storage_path   = None
        self._writable       = writable
        self._recalc         = recalc
        self._verbose        = verbose
        self._files_seen     = set()
        self._integrity_dict = {}

    @property
    def storage_path(self):
        return self._storage_path

    @property
    def known_files(self):
        return list(self._integrity_dict.keys())

    @property
    def seen_files(self):
        return self._files_seen

    def _get_file_path(self, file_name):
        return os.path.join(self._root, file_name)

    def _load(self):
        raise RuntimeError("Not Implemented")

    def _save(self):
        raise RuntimeError("Not Implemented")

    def _calculate(self, file_name):
        raise RuntimeError("Not Implemented")

    def _verify(self, file_name):
        raise RuntimeError("Not Implemented")

    def _delete(self, file_name):
        raise RuntimeError("Not Implemented")

    def load(self, root):
        self._root           = root
        self._files_seen     = set()
        self._integrity_dict = {}
        self._storage_path   = os.path.join(self._root, self._storage_name)
        self._load()

    def save(self):
        if not self._writable:
            return RESULT_ERROR

        self._save()
        return RESULT_OK

    def calculate(self, file_name):
        self._files_seen.add(file_name)

        if (file_name in self._integrity_dict) and (not self._recalc):
            return RESULT_SKIP

        # pylint: disable=assignment-from-no-return
        result, file_integrity = self._calculate(file_name)

        if result == RESULT_OK:
            self._integrity_dict[file_name] = file_integrity

        return result

    def verify(self, file_name):
        self._files_seen.add(file_name)

        if file_name not in self._integrity_dict:
            return RESULT_NEW

        return self._verify(file_name)

    def repair(self, file_name):
        raise RuntimeError("Not Implemented")

    def mark_as_seen(self, file_name):
        self._files_seen.add(file_name)

    def prune(self):
        result = []

        # NOTE: need to cache file names in case dict is modified in the loop
        original_files = list(self._integrity_dict.keys())

        for file_name in original_files:
            if file_name not in self._files_seen:
                file_path = os.path.join(self._root, file_name)

                if self._delete(file_name) == RESULT_OK:
                    result.append(file_path)
                    self._integrity_dict.pop(file_name)

        return result

