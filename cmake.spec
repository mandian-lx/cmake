%define shortVersion %(echo %{version} | cut -d. -f1,2)

%ifnarch aarch64
%bcond_with	bootstrap
%else
%bcond_without	bootstrap
%endif

Name:		cmake
Summary:	Cross-platform, open-source make system
Version:	3.0.2
Release:	2
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
BuildRequires:	qmake5
BuildRequires:	pkgconfig(Qt5Gui)
BuildRequires:	pkgconfig(Qt5Widgets)
BuildRequires:	qt5-platformtheme-gtk2
# Ensure tests of Qt5Gui's cmake builds don't result in an error
# because libqdirectfb.so and friends have been "removed" since creating the
# cmake module
BuildRequires:	%{mklibname qt5gui 5}-offscreen
BuildRequires:	%{mklibname qt5gui 5}-x11
BuildRequires:	%{mklibname qt5gui 5}-linuxfb
BuildRequires:	%{mklibname qt5gui 5}-minimal
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
%{_datadir}/%{name}
%{_sysconfdir}/emacs/site-start.d/%{name}.el
%{_sysconfdir}/rpm/macros.d/*
%{_datadir}/emacs/site-lisp/cmake-mode.el
%{_datadir}/vim/*/*
%{_datadir}/aclocal/cmake.m4
%doc CMakeLogo.gif mydocs/*

#-----------------------------------------------------------------------------

%if !%{with bootstrap}
%package -n	%{name}-qtgui
Summary:	Qt GUI Dialog for CMake - the Cross-platform, open-source make system
Group:		Development/Other
Requires:	%{name}
# (tpg) Fix for bug https://issues.openmandriva.org/show_bug.cgi?id=833
Requires:	%{_lib}qt5gui5
Requires:	%{_lib}xcb-util-renderutil0
Requires:	%{_lib}xcb-icccm4

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
mkdir -p %{buildroot}%{_datadir}/emacs/site-lisp %{buildroot}%{_sysconfdir}/emacs/site-start.d
mv %{buildroot}%{_datadir}/cmake/editors/emacs/cmake-mode.el %{buildroot}%{_datadir}/emacs/site-lisp/cmake-mode.el
cat <<EOF >%{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.el
(setq load-path (cons (expand-file-name "/dir/with/cmake-mode") load-path))
(require 'cmake-mode)
(setq auto-mode-alist
      (append '(("CMakeLists\\\\.txt\\\\'" . cmake-mode)
                ("\\\\.cmake\\\\'" . cmake-mode))
              auto-mode-alist))
EOF

# cmake mode for vim
mkdir -p %{buildroot}%{_datadir}/vim/syntax %{buildroot}%{_datadir}/vim/indent %{buildroot}%{_datadir}/vim/plugin
mv %{buildroot}%{_datadir}/cmake/editors/vim/cmake-syntax.vim %{buildroot}%{_datadir}/vim/syntax/cmake.vim
mv %{buildroot}%{_datadir}/cmake/editors/vim/cmake-indent.vim %{buildroot}%{_datadir}/vim/indent/cmake.vim
mv %{buildroot}%{_datadir}/cmake/editors/vim/cmake-help.vim %{buildroot}%{_datadir}/vim/plugin/cmake-help.vim

# remove directory we just cleared by moving files where editors
# will actually find them
rm -rf %{buildroot}%{_datadir}/cmake/editors

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
