#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil, os
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class EglConan(ConanFile):
    name            = 'egl'
    version         = '2.1'
    license         = 'MIT'
    url             = 'https://github.com/kheaactua/conan-egl.git'
    description     = 'https://www.mesa3d.org/intro.html'
    md5_hash        = '66afbc1dddcaa4c7dabf5c5ee187c73b'
    requires        = (
        'libdrm/[>=2.4.75]@ntc/stable',
        'helpers/[>=0.3]@ntc/stable',
    )
    generators = 'virtualenv'
    use_scons = True

    settings = {
        'compiler': None,
        'os_build':   ['Linux'],
        'arch_build': ['x86_64'],
        'build_type': None,
    }

    def system_requirements(self):
        pack_names = None
        if 'ubuntu' == tools.os_info.linux_distro:
            pack_names = ['libelf-dev']

        if pack_names:
            installer = tools.SystemPackageTool()
            try:
                # installer.update() # Update the package database
                installer.install(' '.join(pack_names)) # Install the package
            except ConanException:
                self.output.warn('Could not run system requirements installer.  Required packages might be missing.')

    def build_requirements(self):
        pack_names = None
        if 'ubuntu' == tools.os_info.linux_distro:
            pack_names = ['autoconf', 'autopoint', 'automake', 'autotools-dev', 'libtool', 'autopoint', 'libyaml-dev', 'python-mako']

            self.output.info('If you receive an issue with mako, run:\n pip install prettytable Mako pyaml dateutils --upgrade\n\nIf it persists, also try:\nsudo apt-get install python-mako')

        if pack_names:
            installer = tools.SystemPackageTool()
            try:
                # installer.update() # Update the package database
                installer.install(' '.join(pack_names)) # Install the package
            except ConanException:
                self.output.warn('Could not run build requirements installer.')

        # We need >2.4, 14.04 has 2.3.  Maybe only do this if we have to (implement detection?)
        self.build_requires('scons/[>=2.4]@ntc/stable')

    def source(self):
        archive = 'mesa-18.%s'%self.version
        archive_file = '%s.tar.xz'%archive
        url = 'https://mesa.freedesktop.org/archive/%s'%archive_file

        from source_cache import copyFromCache
        if not copyFromCache(archive_file):
            tools.download(url=url, filename=archive_file)
            tools.check_md5(archive_file, self.md5_hash)
        tools.unzip(archive_file)
        shutil.move(archive, self.name)
        os.remove(archive_file)

    def build(self):
        # Ensure the conan paths are first in the environment
        if 'PKG_CONFIG_PATH' in os.environ:
            from platform_helpers import reorderPkgConfigPath
            os.environ['PKG_CONFIG_PATH'] = reorderPkgConfigPath(os.environ['PKG_CONFIG_PATH'], self)

        s = '\npkg-config Environment:\n'
        for k,v in os.environ.items():
            if 'PKG_CONFIG' in k:
                s += ' - %s=%s\n'%(k, v)
        self.output.info(s)
        self.output.info('PATH=%s'%os.environ['PATH'])

        with tools.chdir(self.name):
            if self.use_scons:
                self._scons_build()
            else:
                self._autotools_build()

    def _scons_build(self):
        env = {'build': str(self.settings.build_type).lower()}
        with tools.environment_append(env):
            self.run('scons .')

    def _autotools_build(self):
        """ Can't seem to get it to build yet: undeclared sys_memfd_create """

        args = []
        args.append('--prefix=%s'%self.package_folder)
        args.append('--enable-egles')
        args.append('--enable-egles2')
        args.append('--with-platforms=%s'%','.join(['x11']))
        args.append('--enable-shared-glapi')

        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(args=args)
        autotools.make()
        autotools.install()

    def package(self):
        if self.use_scons:
            self._scons_package()

    def _scons_package(self):
        # No idea why it's 'debug', that's probably a problem..
        src = os.path.join(self.build_folder, self.name, 'build', 'linux-x86_64-debug')
        self.output.info('Copying from %s'%src)
        files = os.listdir(src)
        for file_name in files:
            full_file_name = os.path.join(src, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, self.package_folder)
            elif os.path.isdir(full_file_name):
                shutil.copytree(full_file_name, os.path.join(self.package_folder, os.path.basename(full_file_name)))

# vim: ts=4 sw=4 expandtab ffs=unix ft=python foldmethod=marker :
