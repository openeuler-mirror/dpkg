%global enable_dev_package 0

Name:		dpkg
Version:	1.18.25
Release:	10
Summary:	Package maintenance system for Debian Linux
License:	GPLv2 and GPLv2+ and LGPLv2+ and Public Domain and BSD
URL:		https://tracker.debian.org/pkg/dpkg
Source0:	http://ftp.debian.org/debian/pool/main/d/%{name}/%{name}_%{version}.tar.xz

BuildRequires:	zlib-devel bzip2-devel libselinux-devel gettext ncurses-devel
BuildRequires:	autoconf automake doxygen gettext-devel gcc-c++ libtool
BuildRequires:	flex fakeroot xz-devel dotconf-devel po4a >= 0.43
BuildRequires:	perl-interpreter
BuildRequires:	perl-devel
BuildRequires:	perl-generators
BuildRequires:	perl-Time-Piece
BuildRequires:	perl(Digest)
BuildRequires:	perl(Test::More)
BuildRequires:	perl(IPC::Cmd)
BuildRequires:	perl(Digest::SHA)
BuildRequires:	perl(IO::String)
Requires(post): coreutils

Patch1:		dpkg-fix-logrotate.patch
Patch2:		dpkg-log-Change-logfile-permission-to-satisfy-with-s.patch

%description
Dpkg is a tool to install, build, remove and manageDebian packages. The 
primary and more user-friendly front-end for dpkg is aptitude.

%package devel
Summary:	Development package for dpkg
Provides:	dpkg-static = %{version}-%{release}

%description devel
The development package for dpkg.

%if %{enable_dev_package}
%package dev
Summary:	Debian package development tools
Requires:	dpkg-perl = %{version}-%{release} binutils bzip2 lzma
Requires:	make patch xz
Obsoletes:	dpkg-devel < 1.16
BuildArch:	noarch

%description dev
Debian package development tools for dpdk.
%endif

%package perl
Summary:	Dpkg perl modules pacakge
Requires:	dpkg = %{version}-%{release}
Requires:	perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))
Requires:	perl(Digest::SHA) perl(Digest::SHA1) perl(Digest::SHA3)
Requires:	perl-TimeDate perl-Time-Piece perl(Digest::MD5)
BuildArch: 	noarch

%description perl
This package contains dpdk perl modules.

%package help
Summary: Help documents for dpkg
%description help
The help documents for dpkg.

%prep
%autosetup -n %{name}-%{version} -p1

cat << \EOF > %{name}-req
#!/bin/sh
%{__perl_requires} $* |\
  sed -e '/perl(Dselect::Ftp)/d' -e '/perl(extra)/d' -e '/perl(file)/d' -e '/perl(dpkg-gettext.pl)/d' -e '/perl(controllib.pl)/d' -e '/perl(in)/d'
EOF

%define __perl_requires %{_builddir}/%{name}-%{version}/%{name}-req
chmod +x %{__perl_requires}

sed -i 's/^use --/may use --/' scripts/dpkg-source.pl

%build
autoreconf
%configure --disable-linker-optimisations \
        --with-admindir=%{_localstatedir}/lib/dpkg \
        --with-libselinux \
        --without-libmd \
        --with-libz \
        --with-liblzma \
        --with-libbz2

%make_build

%install
%make_install

mkdir -p %{buildroot}/%{_sysconfdir}/logrotate.d
install -pm0644 debian/dpkg.cfg %{buildroot}/%{_sysconfdir}/dpkg
install -pm0644 debian/dselect.cfg %{buildroot}/%{_sysconfdir}/dpkg
install -pm0644 debian/shlibs.default %{buildroot}/%{_sysconfdir}/dpkg
install -pm0644 debian/shlibs.override %{buildroot}/%{_sysconfdir}/dpkg
install -pm0644 debian/dpkg.logrotate %{buildroot}/%{_sysconfdir}/logrotate.d/%{name}

%find_lang dpkg
%find_lang dpkg-dev
%find_lang dselect

%check
make VERBOSE=1 TESTSUITEFLAGS=--verbose TEST_PARALLEL=4 check || :

%post
cd ${DPKG_ADMINDIR:-/var/lib/dpkg}
for file in diversions statoverride status; do
if [ ! -f "$file" ]; then
    touch "$file"
fi
done

touch /var/log/dpkg.log
chmod 640 /var/log/dpkg.log
chown root:root /var/log/dpkg.log 2>/dev/null || chown 0:0 /var/log/dpkg.log

%files -f dpkg.lang -f dselect.lang
%license debian/copyright
%dir %{_sysconfdir}/dpkg
%dir %{_sysconfdir}/dpkg/dpkg.cfg.d
%dir %{_sysconfdir}/dpkg/dselect.cfg.d
%config(noreplace) %{_sysconfdir}/dpkg/dpkg.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/dpkg
%config(noreplace) %{_sysconfdir}/dpkg/dselect.cfg
%{_bindir}/dpkg
%{_bindir}/dpkg-deb
%{_bindir}/dpkg-divert
%{_bindir}/dpkg-maintscript-helper
%{_bindir}/dpkg-query
%{_bindir}/dpkg-split
%{_bindir}/dpkg-statoverride
%{_bindir}/dpkg-trigger
%{_bindir}/dselect
%{_sbindir}/start-stop-daemon
%dir %{_datadir}/dpkg
%{_datadir}/dpkg/abitable
%{_datadir}/dpkg/cputable
%{_datadir}/dpkg/ostable
%{_datadir}/dpkg/tupletable
%dir %{_localstatedir}/lib/dpkg
%dir %{_localstatedir}/lib/dpkg/alternatives
%dir %{_localstatedir}/lib/dpkg/info
%dir %{_localstatedir}/lib/dpkg/parts
%dir %{_localstatedir}/lib/dpkg/updates
%dir %{_localstatedir}/lib/dpkg/methods

%exclude %{_libdir}/libdpkg.la
%exclude %{_bindir}/update-alternatives
%exclude %{_sysconfdir}/alternatives/
%if %{enable_dev_package}
%exclude %{_sbindir}/install-info
%endif
%if !%{enable_dev_package}
%exclude %{_bindir}/dpkg-architecture
%exclude %{_bindir}/dpkg-buildpackage
%exclude %{_bindir}/dpkg-buildflags
%exclude %{_bindir}/dpkg-checkbuilddeps
%exclude %{_bindir}/dpkg-distaddfile
%exclude %{_bindir}/dpkg-genbuildinfo
%exclude %{_bindir}/dpkg-genchanges
%exclude %{_bindir}/dpkg-gencontrol
%exclude %{_bindir}/dpkg-gensymbols
%exclude %{_bindir}/dpkg-mergechangelogs
%exclude %{_bindir}/dpkg-name
%exclude %{_bindir}/dpkg-parsechangelog
%exclude %{_bindir}/dpkg-scanpackages
%exclude %{_bindir}/dpkg-scansources
%exclude %{_bindir}/dpkg-shlibdeps
%exclude %{_bindir}/dpkg-source
%exclude %{_bindir}/dpkg-vendor
%exclude %{_datadir}/dpkg/*.mk
%exclude /etc/dpkg/shlibs.*
%exclude /usr/share/locale/ca/LC_MESSAGES/dpkg-dev.mo
%exclude /usr/share/locale/de/LC_MESSAGES/dpkg-dev.mo
%exclude /usr/share/locale/es/LC_MESSAGES/dpkg-dev.mo
%exclude /usr/share/locale/fr/LC_MESSAGES/dpkg-dev.mo
%exclude /usr/share/locale/pl/LC_MESSAGES/dpkg-dev.mo
%exclude /usr/share/locale/ru/LC_MESSAGES/dpkg-dev.mo
%exclude /usr/share/locale/sv/LC_MESSAGES/dpkg-dev.mo
%endif

%{perl_vendorlib}/Dselect
%{_libexecdir}/dpkg/methods

%files devel
%{_libdir}/libdpkg.a
%{_libdir}/pkgconfig/libdpkg.pc
%{_includedir}/dpkg/*.h

%if %{enable_dev_package}
%files dev -f dpkg-dev.lang
%config(noreplace) %{_sysconfdir}/dpkg/shlibs.default
%config(noreplace) %{_sysconfdir}/dpkg/shlibs.override
%{_bindir}/dpkg-architecture
%{_bindir}/dpkg-buildpackage
%{_bindir}/dpkg-buildflags
%{_bindir}/dpkg-checkbuilddeps
%{_bindir}/dpkg-distaddfile
%{_bindir}/dpkg-genbuildinfo
%{_bindir}/dpkg-genchanges
%{_bindir}/dpkg-gencontrol
%{_bindir}/dpkg-gensymbols
%{_bindir}/dpkg-mergechangelogs
%{_bindir}/dpkg-name
%{_bindir}/dpkg-parsechangelog
%{_bindir}/dpkg-scanpackages
%{_bindir}/dpkg-scansources
%{_bindir}/dpkg-shlibdeps
%{_bindir}/dpkg-source
%{_bindir}/dpkg-vendor
%{_datadir}/dpkg/*.mk
%endif

%files perl
%{perl_vendorlib}/Dpkg*
%{_datadir}/dpkg/*.specs

%files help
%doc debian/changelog README TODO
%doc dselect/methods/multicd/README.multicd
%doc debian/dpkg.cron.daily
%doc AUTHORS THANKS debian/usertags doc/README.api
%doc doc/frontend.txt doc/triggers.txt
%{_mandir}/*
%exclude %{_mandir}/it/man1/
%exclude %{_mandir}/it/man5/
%exclude %{_mandir}/pl/man1/
%if %{enable_dev_package}
%exclude %{_mandir}/man1/update-alternatives.1
%exclude %{_mandir}/*/man1/update-alternatives.1
%endif

%changelog
* Mon Mar 16 2020 openEuler Buildteam <buildteam@openeuler.org> - 1.18.25-10
- disable dpkg-dev

* Wed Sep 11 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.18.25-9
- Package init
