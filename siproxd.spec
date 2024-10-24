%global project_version_major 0
%global project_version_minor 8
%global project_version_patch 3

%global siproxduser     siproxd
%global siproxdgroup    siproxd

Name:          siproxd
Version:       %{project_version_major}.%{project_version_minor}.%{project_version_patch}
Release:       1%{?dist}
Summary:       A SIP masquerading proxy with RTP support
License:       GPL-2.0-or-later

URL:           http://siproxd.sourceforge.net/
Source0:       https://sourceforge.net/projects/siproxd/files/siproxd/%{version}/siproxd-%{version}.tar.gz
Source1:       siproxd.service
Source2:       siproxd.logrotate

Patch0:        acinclude.m4.patch
 
Requires:      libosip2

BuildRequires: libosip2-devel
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: libtool-ltdl-devel
BuildRequires: sqlite-devel
BuildRequires: systemd

Requires(pre): %{_sbindir}/groupadd
Requires(pre): %{_sbindir}/useradd

%description
Siproxd is a proxy/masquerading daemon for SIP (Session Initiation
Protocol), which is used in IP telephony.
It handles registrations of SIP clients on a private IP network
and performs rewriting of the SIP message bodies to make SIP
connections work via a masquerading firewall (NAT).
It allows SIP software clients (like kphone, linphone) or SIP
hardware clients (Voice over IP phones which are SIP-compatible,
such as those from Cisco, Grandstream or Snom) to work behind
an IP masquerading firewall or NAT router.

%prep
%autosetup

%build
autoreconf -vfi
%configure --disable-static
%make_build

%install
%make_install
find %{buildroot} -type f -name "*.la" -delete -print

# Copy config
install -d %{buildroot}%{_sysconfdir}/%{name}
mv %{buildroot}%{_sysconfdir}/%{name}.conf.example %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
# Adapt config
sed -i -e "s@nobody@%{siproxduser}@" %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
sed -i -e "s@/var/run@%{_rundir}@" %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
# Deploy logrotate
install -d %{buildroot}/%{_sysconfdir}/logrotate.d/
install -m 0644 %{_sourcedir}/%{name}.logrotate %{buildroot}/%{_sysconfdir}/logrotate.d/%{name}
# Deploy systemd
install -d %{buildroot}/%{_unitdir}
install -m 644 %{_sourcedir}/%{name}.service %{buildroot}/%{_unitdir}/%{name}.service
sed -i -e "s@/run@%{_rundir}@" %{buildroot}/%{_unitdir}/%{name}.service
install -d %{buildroot}/%{_sbindir}
# Create run directory for pid file
install -d %{buildroot}/%{_rundir}/%{name}
# Install state file directory
install -d %{buildroot}/%{_sharedstatedir}/%{name}
# Cleanup
rm -f %{buildroot}/%{_sysconfdir}/siproxd_passwd.cfg
rm -f %{buildroot}/%{_libdir}/%{name}/*.a
rm -rf %{buildroot}/usr/share/doc/%{name}

%post
%ldconfig_scriptlets
%systemd_post siproxd.service

%pre
%service_add_pre siproxd.service
getent group %{siproxdgroup} >/dev/null || %{_sbindir}/groupadd -r %{siproxdgroup}
getent passwd %{siproxduser} >/dev/null || %{_sbindir}/useradd -r -g %{siproxdgroup} -s /bin/false \ -c "Siproxd user" -d %{_rundir}/%{name} %{siproxduser}

%postun
%systemd_postun_with_restart siproxd.service
%ldconfig_scriptlets

%preun
%systemd_preun siproxd.service

%files
%license COPYING
%doc README AUTHORS ChangeLog
%doc doc/siproxd.conf.example doc/siproxd_passwd.cfg doc/FAQ doc/KNOWN_BUGS doc/sample_*
# Lib
%attr(0755,root,root) %{_libdir}/%{name}/
# Bin
%{_sbindir}/%{name}
# Systemd
%{_unitdir}
%{_unitdir}/siproxd.service
# Config dir
%dir %{_sysconfdir}/%{name}
# Config
%config %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
# Run directory for pid file
%dir %attr(0750,%{siproxduser},root) %{_rundir}/%{name}
# State file directory
%dir %attr(0750,%{siproxduser},root) %{_sharedstatedir}/%{name}

%changelog
%autochangelog
