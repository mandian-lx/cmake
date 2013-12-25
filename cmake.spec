%define shortVersion %(echo %{version} | cut -d. -f1,2)

%bcond_with	bootstrap

Name:		cmake
Summary:	Cross-platform, open-source make system
Version:	2.8.11.2
Release:	5
Epoch:		1
License:	BSD
Group:		Development/Other
Url:		http://www.cmake.org/HTML/index.html
Source0:	http://www.cmake.org/files/v%{shortVersion}/%{name}-%{version}.tar.gz
Source1:	cmake.macros
Source2:	cmake.rpmlintrc
# fix ftlk detection
Patch1:		0001-Fix-FLTK-Find-path.patch
Patch3:		0003-Disable-Test198.patch
# Fix ImageMagick detection (not upstream yet; parts 1 and 2 are)
Patch6:		0003-FindImageMagick-part3.patch
BuildRequires:	perl
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	pkgconfig(libidn)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	xz
BuildRequires:	pkgconfig(expat)
BuildRequires:	bzip2-devel
BuildRequires:	pkgconfig(libarchive)
%if !%{with bootstrap}
BuildRequires:	pkgconfig(QtCore)
%endif
BuildRequires:	gcc-gfortran

%description
CMake is used to control the software compilation process using
simple platform and compiler independent configuration files.
CMake generates native makefiles and workspaces that can be
used in the compiler environment of your choice. CMake is quite
sophisticated: it is possible to support complex environments
requiring system configuration, pre-processor generation, code
generation, and template instantiation.

%files
%{_bindir}/cmake
%{_bindir}/ccmake
%{_bindir}/ctest
%{_bindir}/cpack
%{_mandir}/man1/*
%{_datadir}/%{name}
%{_sysconfdir}/emacs/site-start.d/%{name}.el
%{_sysconfdir}/rpm/macros.d/*
%{_datadir}/emacs/site-lisp/cmake-mode.el
%{_datadir}/vim/*/*
%{_datadir}/aclocal/cmake.m4
%doc CMakeLogo.gif Example mydocs/*

#-----------------------------------------------------------------------------

%if !%{with bootstrap}
%package -n	%{name}-qtgui
Summary:	Qt GUI Dialog for CMake - the Cross-platform, open-source make system
Group:		Development/Other
Requires:	%{name}

%description -n	%{name}-qtgui
CMake is used to control the software compilation process using
simple platform and compiler independent configuration files.

This is the Qt GUI.

%files -n	%{name}-qtgui
%{_bindir}/cmake-gui
%{_datadir}/applications/CMake.desktop
%{_datadir}/mime/packages/cmakecache.xml
%{_datadir}/pixmaps/CMakeSetup32.png
%endif

#-----------------------------------------------------------------------------

%prep
%setup -q
%apply_patches

# Don't try to automagically find files in /usr/X11R6
# But also don't change a prefix if it is not /usr
perl -pi -e 's@^\s+/usr/X11R6/.*\n@@' Modules/*.cmake

%ifarch %{arm}
# bootstrap test is taking ages on arm
sed -i -e 's!SET(CMAKE_LONG_TEST_TIMEOUT 1500)!SET(CMAKE_LONG_TEST_TIMEOUT 7200)!g' Tests/CMakeLists.txt
%endif

%build
mkdir -p build
cd build
%setup_compile_flags
../configure \
    --system-libs \
    --parallel=%{_smp_mflags} \
    --prefix=%{_prefix} \
    --datadir=/share/%{name} \
    --mandir=/share/man \
    --docdir=/share/doc/%{name} \
%if !%{with bootstrap}
    --qt-gui
%endif

%make

%install
%makeinstall_std -C build

# cmake mode for emacs
install -m644 Docs/cmake-mode.el -D %{buildroot}%{_datadir}/emacs/site-lisp/cmake-mode.el
install -d %{buildroot}%{_sysconfdir}/emacs/site-start.d
cat <<EOF >%{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.el
(setq load-path (cons (expand-file-name "/dir/with/cmake-mode") load-path))
(require 'cmake-mode)
(setq auto-mode-alist
      (append '(("CMakeLists\\\\.txt\\\\'" . cmake-mode)
                ("\\\\.cmake\\\\'" . cmake-mode))
              auto-mode-alist))
EOF

# cmake mode for vim
install -m644 Docs/cmake-syntax.vim -D %{buildroot}%{_datadir}/vim/syntax/cmake.vim
install -m644 Docs/cmake-indent.vim -D %{buildroot}%{_datadir}/vim/indent/cmake.vim

# RPM macros
install -m644 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/rpm/macros.d/cmake.macros

# %doc wipes out files in doc dir, fixed in cooker svn for rpm package, though
# not submitted yet, so we'll just work around this by moving it for now..
rm -rf mydocs
mv %{buildroot}%{_datadir}/doc/%{name} mydocs

# As of 2.8.10.2, the test suite needs net access.
# Absent that, it will fail:
# The following tests FAILED:
#        186 - CTestTestFailedSubmit-http (Failed)
#        187 - CTestTestFailedSubmit-https (Failed)
%if 0
%check
unset DISPLAY
cd build
bin/ctest -E SubDirSpaces -V %{_smp_mflags}
%endif
