#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilities regarding temporary storage
"""
import tempfile
import shutil
import os

class AutoDeleteTempfileGenerator(object):
    """
    A wrapper for temporary files and directories that are automatically automatically
    deleted once this class is deleted or deleteAll() is called.

    This is not comparable to tempfile.TemporaryFile as the TemporaryFile instance
    will not guaranteed to be visible in the filesystem and is immediately removed
    once closed. This class will only delete files or directories upon request or upon
    garbage collection.

    Ensure this class does not go out of scope without other references to it unless
    you don't want to use the files any more.
    """
    def __init__(self):
        self.tempdirs = []
        self.tempfiles = []

    def __del__(self):
        self.delete_all()

    def mktemp(self, suffix='', prefix='tmp', dir=None):
        """Same as tempfile.mktemp(), but creates a file managed by this class instance"""
        fname = tempfile.mktemp(suffix, prefix, dir)
        self.tempfiles.append(fname)
        return fname

    def mkdtemp(self, suffix='', prefix='tmp', dir=None):
        """Same as tempfile.mkdtemp(), but creates a file managed by this class instance"""
        fname = tempfile.mkdtemp(suffix, prefix, dir)
        self.tempdirs.append(fname)
        return fname

    def delete_all(self):
        """
        Force-delete all files and directories created by this instance.
        The class instance may be used without restriction after this call
        """
        # 
        for filename in self.tempfiles:
            os.remove(filename)
        # Remove directories via shutil
        for tempdir in self.tempdirs:
            shutil.rmtree(tempdir)
