%define shortVersion %(echo %{version} | cut -d. -f1,2)

%define qt4 0

Name: cmake
Summary: Cross-platform, open-source make system
Version: 2.8.7
Release: 1
License: BSD
Group: Development/Other
Epoch: 1
Url: http://www.cmake.org/HTML/index.html
Source0: http://www.cmake.org/files/v%{shortVersion}/%name-%{version}.tar.gz
Source1: cmake.macros
# fix ftlk detection
Patch1: cmake-fltk-path.patch
Patch2: cmake-2.8.4-xz-support.patch
BuildRequires: perl
BuildRequires: ncurses-devel
BuildRequires: libcurl-devel
BuildRequires: idn-devel
BuildRequires: zlib-devel
BuildRequires: xz
BuildRequires: expat-devel
BuildRequires: bzip2-devel
BuildRequires: libarchive-devel
%if %qt4
BuildRequires: qt4-devel >= 4.4.0
%endif
BuildRequires: gcc-gfortran
Requires: rpm-manbo-setup >= 2-10

%description
CMake is used to control the software compilation process using
simple platform and compiler independent configuration files.
CMake generates native makefiles and workspaces that can be
used in the compiler environment of your choice. CMake is quite
sophisticated: it is possible to support complex environments
requiring system configuration, pre-processor generation, code
generation, and template instantiation.

%files
%_bindir/cmake
%_bindir/ccmake
%_bindir/ctest
%_bindir/cpack
%_mandir/man1/*
%_datadir/%{name}
%_sysconfdir/emacs/site-start.d/%{name}.el
%_sysconfdir/rpm/macros.d/*
%_datadir/emacs/site-lisp/cmake-mode.el
%if %mdkversion > 200900
%_datadir/vim/*/*
%endif
%_datadir/aclocal/cmake.m4
%doc CMakeLogo.gif Example mydocs/*

#-----------------------------------------------------------------------------

%if %qt4
%package -n %{name}-qtgui
Summary:    Qt GUI Dialog for CMake - the Cross-platform, open-source make system
Group:      Development/Other
Requires:   %name

%description -n %{name}-qtgui
CMake is used to control the software compilation process using
simple platform and compiler independent configuration files.

This is the Qt GUI.

%files -n %{name}-qtgui
%_bindir/cmake-gui
%_datadir/applications/CMake.desktop
%_datadir/mime/packages/cmakecache.xml
%_datadir/pixmaps/CMakeSetup32.png
%endif

#-----------------------------------------------------------------------------

%prep
%setup -q
%patch1
%patch2 -p1 -b .xz~

# Don't try to automagically find files in /usr/X11R6
# But also don't change a prefix if it is not /usr
perl -pi -e 's@^\s+/usr/X11R6/.*\n@@' Modules/*.cmake

%ifarch %arm
# bootstrap test is taking ages on arm
sed -i -e 's!SET(CMAKE_LONG_TEST_TIMEOUT 1500)!SET(CMAKE_LONG_TEST_TIMEOUT 7200)!g' Tests/CMakeLists.txt
%endif

%build
mkdir -p build
cd build
%setup_compile_flags
../configure \
    --system-libs \
    --parallel=%_smp_mflags \
    --prefix=%{_prefix} \
    --datadir=/share/%{name} \
    --mandir=/share/man \
    --docdir=/share/doc/%{name} \
%if %qt4
    --qt-gui
%endif

%make

%install
rm -rf %buildroot
pushd build
%makeinstall_std
popd

# cmake mode for emacs
install -m644 Docs/cmake-mode.el -D %buildroot%_datadir/emacs/site-lisp/cmake-mode.el
install -d %buildroot%_sysconfdir/emacs/site-start.d
cat <<EOF >%buildroot%_sysconfdir/emacs/site-start.d/%{name}.el
(setq load-path (cons (expand-file-name "/dir/with/cmake-mode") load-path))
(require 'cmake-mode)
(setq auto-mode-alist
      (append '(("CMakeLists\\\\.txt\\\\'" . cmake-mode)
                ("\\\\.cmake\\\\'" . cmake-mode))
              auto-mode-alist))
EOF

# cmake mode for vim
install -m644 Docs/cmake-syntax.vim -D %buildroot%_datadir/vim/syntax/cmake.vim
install -m644 Docs/cmake-indent.vim -D %buildroot%_datadir/vim/indent/cmake.vim

# RPM macros
install -m644 %SOURCE1 -D %buildroot%_sysconfdir/rpm/macros.d/cmake.macros

# %doc wipes out files in doc dir, fixed in cooker svn for rpm package, though
# not submitted yet, so we'll just work around this by moving it for now..
rm -rf mydocs
mv %buildroot%_datadir/doc/%{name} mydocs

%check
unset DISPLAY
cd build
#bin/ctest -E SubDirSpaces -V %{_smp_mflags}
