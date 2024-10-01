import logging
import os

from .consts import (
    RESULT_OK, RESULT_NEW, RESULT_ERROR, RESULT_MISMATCH, RESULT_SKIP,
    RESULT_DEL
)
from .integrity.par2 import (
    Par2Integrity, PAR2_STORAGE_NAME, PAR2_DEFAULT_ARGS
)
from .integrity.hash import (
    HashIntegrity, SUPPORTED_HASHES, HASH_STORAGE_NAMES
)

LOGGER = logging.getLogger('rik')

DEFAULT_EXCLUDES = [ PAR2_STORAGE_NAME, ] + HASH_STORAGE_NAMES

def select_integrity(name, writable, recalc, verbosity, iargs = None):
    iargs  = iargs or []
    kwargs = {
        'writable' : writable,
        'recalc'   : recalc,
        'verbose'  : (verbosity > 1),
    }

    if name == 'par2':
        integrity = Par2Integrity(
            par2_args = (PAR2_DEFAULT_ARGS + iargs), **kwargs
        )

    elif name in SUPPORTED_HASHES:
        integrity = HashIntegrity(hash_name = name, **kwargs)

    else:
        raise RuntimeError(f"Unknown integrity type: '{name}'")

    return integrity

def check_constraints(path, constraints):
    for constraint in constraints:
        if not constraint.check(path):
            LOGGER.debug("Path '%s' fails constraints. Skipping.", path)
            return False

    return True

def verify_integrity(file_name, file_path, integrity, result_dict):
    try:
        result = integrity.verify(file_name)
    except OSError as e:
        LOGGER.error(e)
        result = RESULT_ERROR

    result_dict[file_path] = result

    if result == RESULT_MISMATCH:
        LOGGER.warning("Integrity mismatch for: '%s'", file_path)
    elif result == RESULT_NEW:
        LOGGER.warning("New File: '%s'", file_path)
    elif result == RESULT_ERROR:
        LOGGER.warning("Failed to verify file: '%s'", file_path)
    elif result == RESULT_OK:
        LOGGER.info("File ok: '%s'", file_path)
    else:
        LOGGER.error("Unknown return code '%d' for '%s'", result, file_path)

def create_integrity(file_name, file_path, integrity, result_dict):
    try:
        result = integrity.calculate(file_name)
    except OSError as e:
        LOGGER.error(e)
        result = RESULT_ERROR

    result_dict[file_path] = result

    if result == RESULT_ERROR:
        LOGGER.warning("Failed to create integrity for: %s", file_path)
    elif result == RESULT_SKIP:
        LOGGER.debug("Integrity for '%s' has already been created", file_path)
    elif result == RESULT_OK:
        LOGGER.info("Successfully created integrity for file %s", file_path)
    else:
        LOGGER.error("Unknown return code '%d' for %s", result, file_path)

def handle_file(
    file_name, file_path, integrity, constraints, result_dict,
    create = False, verify = False
):
    # pylint: disable=too-many-arguments

    if not os.path.isfile(file_path):
        LOGGER.debug("Path '%s' is not a file. Skipping.", file_path)
        return

    if (not create) and (not verify):
        integrity.mark_as_seen(file_name)
        return

    if not check_constraints(file_path, constraints):
        result_dict[file_path] = RESULT_SKIP
        return

    if create:
        create_integrity(file_name, file_path, integrity, result_dict)

    if verify:
        verify_integrity(file_name, file_path, integrity, result_dict)

def walk_filesystem(
    root_dir, integrity, dir_constraints, file_constraints,
    create, prune, verify
):
    # pylint: disable=too-many-arguments
    result_dict = {}

    for root, _dirs, files in os.walk(root_dir):

        if not check_constraints(root, dir_constraints):
            continue

        LOGGER.info("Processing directory '%s'", root)
        try:
            integrity.load(root)
        except IOError:
            result_dict[root] = RESULT_ERROR
            continue

        for file_name in files:
            file_path = os.path.join(root, file_name)
            handle_file(
                file_name, file_path, integrity, file_constraints, result_dict,
                create, verify
            )

        if prune:
            for file_path in integrity.prune():
                LOGGER.info("Pruned: '%s'", file_path)
                result_dict[file_path] = RESULT_DEL

        if create or prune:
            try:
                integrity.save()
            except IOError:
                result_dict[root] = RESULT_ERROR
                continue

    return result_dict

def print_summary_block(result_dict, value, title):
    matching_files = [ k for (k, v) in result_dict.items() if v == value ]

    if matching_files:
        print('    ', title)
        for file_path in matching_files:
            print('    ', '    ', file_path)

    return len(matching_files)

def print_summary(result_dict):
    print("SUMMARY")

    n_ok   = print_summary_block(result_dict, RESULT_OK,       "Successful")
    n_new  = print_summary_block(result_dict, RESULT_NEW,      "New")
    n_del  = print_summary_block(result_dict, RESULT_DEL,      "Removed")
    n_skip = print_summary_block(result_dict, RESULT_SKIP,     "Skipped")
    n_err  = print_summary_block(result_dict, RESULT_ERROR,    "Error")
    n_mis  = print_summary_block(result_dict, RESULT_MISMATCH, "Mismatch")

    print(
        f"\nTotal: {len(result_dict)}."
        f" OK: {n_ok}. NEW: {n_new}. DEL: {n_del}."
        f" SKIP: {n_skip}. FAIL: {n_mis}. ERROR: {n_err}."
    )

