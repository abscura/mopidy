from __future__ import unicode_literals

import argparse
import sys

from mopidy import config as config_lib, ext
from mopidy.utils import deps, versioning


def config_override_type(value):
    try:
        return config_lib.parse_override(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            '%s must have the format section/key=value' % value)


parser = argparse.ArgumentParser()
parser.add_argument(
    '--version', action='version',
    version='Mopidy %s' % versioning.get_version())
parser.add_argument(
    '-q', '--quiet',
    action='store_const', const=0, dest='verbosity_level',
    help='less output (warning level)')
parser.add_argument(
    '-v', '--verbose',
    action='count', default=1, dest='verbosity_level',
    help='more output (debug level)')
parser.add_argument(
    '--save-debug-log',
    action='store_true', dest='save_debug_log',
    help='save debug log to "./mopidy.log"')
parser.add_argument(
    '--show-config',
    action='store_true', dest='show_config',
    help='show current config')
parser.add_argument(
    '--show-deps',
    action='store_true', dest='show_deps',
    help='show dependencies and their versions')
parser.add_argument(
    '--config',
    action='store', dest='config',
    default=b'$XDG_CONFIG_DIR/mopidy/mopidy.conf',
    help='config files to use, colon seperated, later files override')
parser.add_argument(
    '-o', '--option',
    action='append', dest='overrides', type=config_override_type,
    help='`section/key=value` values to override config options')


def show_config(args):
    """Prints the effective config and exits."""
    files = vars(args).get('config', b'').split(b':')
    overrides = vars(args).get('overrides', [])

    extensions = ext.load_extensions()
    config, errors = config_lib.load(files, extensions, overrides)

    # Clear out any config for disabled extensions.
    for extension in extensions:
        if not ext.validate_extension(extension):
            config[extension.ext_name] = {b'enabled': False}
            errors[extension.ext_name] = {
                b'enabled': b'extension disabled its self.'}
        elif not config[extension.ext_name]['enabled']:
            config[extension.ext_name] = {b'enabled': False}
            errors[extension.ext_name] = {
                b'enabled': b'extension disabled by config.'}

    print config_lib.format(config, extensions, errors)
    sys.exit(0)


def show_deps():
    """Prints a list of all dependencies and exits."""
    print deps.format_dependency_list()
    sys.exit(0)
