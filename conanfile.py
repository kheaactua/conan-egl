#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class EglConan(ConanFile):
    name            = 'egl'
    version         = '2.1'
    license         = 'MIT'
    url             = 'https://github.com/kheaactua/conan-egl.git'
    description     = 'https://www.mesa3d.org/intro.html'
    md5_hash        = '66afbc1dddcaa4c7dabf5c5ee187c73b'
    requires        = 'helpers/[>=0.3]@ntc/stable',

    settings = {
        'compiler': None,
        'os_build':   ['Linux'],
        'arch_build': ['x86_64'],
        'build_type': None,
    }

    def system_requirements(self):
        pack_names = None
        if 'ubuntu' == tools.os_info.linux_distro:
            pack_names = [
                'libdrm-dev' # Won't be met on 14.04
            ]

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
            pack_names = ['autoconf', 'autopoint', 'automake', 'autotools-dev', 'libtool', 'autopoint']

        if pack_names:
            installer = tools.SystemPackageTool()
            try:
                # installer.update() # Update the package database
                installer.install(' '.join(pack_names)) # Install the package
            except ConanException:
                self.output.warn('Could not run build requirements installer.')

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

    def build(self):
        args = []
        args.append('--prefix=%s'%self.package_folder)
        args.append('--enable-egles')
        args.append('--enable-egles2')
        args.append('--with-platforms=%s'%','.join(['x11', 'wayland']))
        args.append('--enable-shared-glapi')

        autotools = AutoToolsBuildEnvironment(self)

        with tools.chdir(self.name):
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

# vim: ts=4 sw=4 expandtab ffs=unix ft=python foldmethod=marker :
