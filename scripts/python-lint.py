#!/usr/bin/env python

"""
Enforces Python coding standards via pep8, pyflakes and pylint


Installation:
pip install pep8       - style guide
pip install pep257     - for docstrings
pip install pyflakes   - unused imports and variable declarations
pip install plumbum    - used for executing shell commands

This script can be called from the git pre-commit hook with a
--git-precommit option
"""

import os
import pep257
import re
import sys
from plumbum import local, cli, commands


def lint(to_lint):
    """

    Run all linters against a list of files.

    :param to_lint: a list of files to lint.

    """
    exit_code = 0
    for linter, options in (('pyflakes', []), ('pep8', [])):
        try:
            output = local[linter](*(options + to_lint))
        except commands.ProcessExecutionError as e:
            output = e.stdout

        if output:
            exit_code = 1
            print "{0} Errors:".format(linter)
            print output

    output = hacked_pep257(to_lint)
    if output:
        exit_code = 1
        print "Docstring Errors:".format(linter.upper())
        print output

    if exit_code != 0:
        print ('\nPlease fix these problems commiting, or to ignore them, '
               'use git commit --no-verify')
        sys.exit(exit_code)


def hacked_pep257(to_lint):
    """
    Check for the presence of docstrings, but ignore some of the options
    """
    def ignore(*args, **kwargs):
        pass

    pep257.check_blank_before_after_class = ignore
    pep257.check_blank_after_last_paragraph = ignore
    pep257.check_blank_after_summary = ignore
    pep257.check_ends_with_period = ignore
    pep257.check_one_liners = ignore

    errors = []
    for filename in to_lint:
        with open(filename) as f:
            errors.extend(pep257.check_source(f.read(), filename))
    return '\n'.join([str(error) for error in sorted(errors)])


class Lint(cli.Application):

    """
    Command line app for VmrunWrapper
    """

    DESCRIPTION = "Lints python with pep8, pep257, and pyflakes"

    git = cli.Flag("--git-precommit", help="Lint only modified git files",
                   default=False)

    def main(self, *directories):
        """
        The actual logic that runs the linters
        """
        if not self.git and len(directories) == 0:
            print ("ERROR: At least one directory must be provided (or the "
                   "--git-precommit flag must be passed.\n")
            self.help()
            return

        if len(directories) > 0:
            find = local['find']
            files = []
            for directory in directories:
                real = os.path.expanduser(directory)
                if not os.path.exists(real):
                    raise ValueError("{0} does not exist".format(directory))
                files.extend(find(real, '-name', '*.py').strip().split('\n'))
            if len(files) > 0:
                print "Linting {0} python files.\n".format(len(files))
                lint(files)
            else:
                print "No python files found to lint.\n"

        else:
            status = local['git']('status', '--porcelain', '-uno')
            root = local['git']('rev-parse', '--show-toplevel').strip()

            # get all modified or added python files
            modified = re.findall(r"^[AM]\s+\S+\.py$", status, re.MULTILINE)

            # now just get the path part, which all should be relative to the
            # root
            files = [os.path.join(root, line.split(' ', 1)[-1].strip())
                     for line in modified]
            if len(files) > 0:
                lint(files)


if __name__ == "__main__":
    Lint.run()
