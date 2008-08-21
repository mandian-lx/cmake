%define shortVersion %(echo %{version} | cut -d. -f1,2)

Name: cmake
Summary: Cross-platform, open-source make system
Version: 2.6.1
Release: %mkrel 1
License: BSD
Group: Development/Other
Epoch: 1
Url: http://www.cmake.org/HTML/index.html
Source: http://www.cmake.org/files/v%{shortVersion}/%name-%{version}.tar.gz
Source1: cmake.macros
# fix vtk 5.0 detection
Patch0: cmake-vtk-5.0.patch
# fix ftlk detection
Patch1: cmake-fltk-path.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: chrpath
BuildRequires: perl
BuildRequires: ncurses-devel
Requires: rpm-manbo-setup >= 2-10

%description
CMake is used to control the software compilation process using
simple platform and compiler independent configuration files.
CMake generates native makefiles and workspaces that can be
used in the compiler environment of your choice. CMake is quite
sophisticated: it is possible to support complex environments
requiring system configuration, pre-processor generation, code
generation, and template instantiation.

%prep

%setup -q -n %name-%{version}
%patch0
%patch1

%if "%{_lib}" != "lib"
perl -pi -e 's#usr/lib#usr/lib64#' `find -type f`
perl -pi -e 's#/usr/X11R6/lib#/usr/X11R6/lib64#' `find -type f`
%endif

# Don't try to automagically find files in /usr/X11R6
# But also don't change a prefix if it is not /usr
perl -pi -e 's@^\s+/usr/X11R6/.*\n@@' Modules/*.cmake

%build
./configure \
	--prefix=%{_prefix} \
	--mandir=/share/man

%make

%install
rm -rf %buildroot
make install DESTDIR=%buildroot

# cmake mode for emacs
install -d %buildroot%_datadir/emacs/site-lisp/
install -m644 Docs/cmake-mode.el %buildroot%_datadir/emacs/site-lisp/
install -d %buildroot%_sysconfdir/emacs/site-start.d
cat <<EOF >%buildroot%_sysconfdir/emacs/site-start.d/%{name}.el
(setq load-path (cons (expand-file-name "/dir/with/cmake-mode") load-path))
(require 'cmake-mode)
(setq auto-mode-alist
      (append '(("CMakeLists\\\\.txt\\\\'" . cmake-mode)
                ("\\\\.cmake\\\\'" . cmake-mode))
              auto-mode-alist))
EOF

install -d -m 755 %buildroot%_sysconfdir/rpm/macros.d/
install -m 644 %SOURCE1 %buildroot%_sysconfdir/rpm/macros.d/
for name in Docs/ctest.1 Docs/cmake.1 Docs/ccmake.1 Docs/cmake-mode.el Docs/cmake-indent.vim Docs/cmake-syntax.vim; do
    rm -f ${name}
done

%clean
rm -rf %buildroot

%files
%defattr(-,root,root)
%_bindir/cmake
%_bindir/ccmake
%_bindir/ctest
%_bindir/cpack
%_mandir/man1/*
%_datadir/cmake-%shortVersion/
%_sysconfdir/emacs/site-start.d/%{name}.el
%_sysconfdir/rpm/macros.d/*
%_datadir/emacs/site-lisp/cmake-mode.el
%doc CMakeLogo.gif ChangeLog.txt Docs/* Example
%exclude %_prefix/doc
