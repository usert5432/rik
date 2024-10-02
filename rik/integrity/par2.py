import os
import re
import shutil
import subprocess

from ..consts   import RESULT_OK, RESULT_ERROR, RESULT_NEW, RESULT_MISMATCH
from .integrity import Integrity

PAR2_CMDNAME      = 'par2'
PAR2_STORAGE_NAME = '.par2'
PAR2_RESULT_EXT   = 'par2'
PAR2_DEFAULT_ARGS = [ '-s524288' ]

class Par2Integrity(Integrity):

    def __init__(
        self,
        writable  = False,
        recalc    = False,
        verbose   = True,
        par2_args = None,
    ):
        super().__init__(PAR2_STORAGE_NAME, writable, recalc, verbose)

        if par2_args is None:
            par2_args = PAR2_DEFAULT_ARGS

        self._par2_args = par2_args
        self.verify_par2_exists()

    def verify_par2_exists(self):
        result = shutil.which(PAR2_CMDNAME)
        if result is None:
            raise RuntimeError(
                f"par2 application '{PAR2_CMDNAME}' is not found in system"
                " $PATH. Make sure that par2 is installed"
            )

    def _get_par2_archive_name(self, file_name):
        return os.path.join(
            self._storage_path, f"{file_name}.{PAR2_RESULT_EXT}"
        )

    def _load(self):
        if not os.path.isdir(self._storage_path):
            return

        archive_part_regexp = re.compile(
            r'^.+\.vol\d+\+\d+\.' + re.escape(PAR2_RESULT_EXT) + r'$'
        )

        ext = '.' + PAR2_RESULT_EXT

        for name in os.listdir(self._storage_path):
            path = os.path.join(self._storage_path, name)

            if not os.path.isfile(path):
                continue

            if not name.endswith(ext):
                continue

            if archive_part_regexp.match(name):
                continue

            file_name = name[:len(name) - len(ext)]
            self._integrity_dict[file_name] = path

    def _calculate(self, file_name):
        if not self._writable:
            return RESULT_ERROR, None

        if not os.path.isdir(self._storage_path):
            try:
                os.mkdir(self._storage_path)
            except OSError:
                return RESULT_ERROR, None

        archive_path = self._get_par2_archive_name(file_name)
        file_path    = self._get_file_path(file_name)

        par2_args = [
            PAR2_CMDNAME, 'create',
            '-a', archive_path,
            '-B', self._root,
            *self._par2_args,
            '--', file_path
        ]

        output = None if self._verbose else subprocess.DEVNULL

        # pylint: disable=(subprocess-run-check)
        result = subprocess.run(
            par2_args,
            stdout = output,
            shell  = False
        )

        # pylint: disable=no-else-return
        if result.returncode == 0:
            return (RESULT_OK, archive_path)
        else:
            return (RESULT_ERROR, archive_path)

    def _verify(self, file_name):
        archive_path = self._get_par2_archive_name(file_name)

        if not os.path.isfile(archive_path):
            return RESULT_NEW

        par2_args = [
            PAR2_CMDNAME, 'verify',
            '-B', self._root,
            '--', archive_path
        ]

        output = None if self._verbose else subprocess.DEVNULL

        # pylint: disable=(subprocess-run-check)
        result = subprocess.run(
            par2_args,
            stdout = output,
            shell  = False
        )

        # pylint: disable=no-else-return
        if result.returncode == 0:
            return RESULT_OK
        else:
            return RESULT_MISMATCH

    def _delete(self, file_name):

        if not self._writable:
            return RESULT_ERROR

        par2_archive_regexp = re.compile(
            r'^(?:\.vol\d+\+\d+)?\.' + re.escape(PAR2_RESULT_EXT) + r'$'
        )

        result = RESULT_OK

        for name in os.listdir(self._storage_path):
            path = os.path.join(self._storage_path, name)

            if not os.path.isfile(path):
                continue

            if not name.startswith(file_name):
                continue

            name_suffix = name[len(file_name):]

            if par2_archive_regexp.match(name_suffix):
                try:
                    os.remove(path)
                except OSError:
                    result = RESULT_ERROR

        return result

    def _save(self):
        if not self._integrity_dict:
            if os.path.isdir(self._storage_path):
                os.rmdir(self._storage_path)

