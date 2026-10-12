# Fox Explorer 6 RPM — packages a tarball made by scripts/build-repack.sh or build-from-source.sh
%global appdir %{_libdir}/foxexplorer6
%{!?_metainfodir:%global _metainfodir %{_datadir}/metainfo}
# Firefox ships its own copies of NSS, libxul etc.; don't export or auto-require them.
%global __provides_exclude_from ^%{appdir}/.*$
%global __requires_exclude_from ^%{appdir}/.*$
%global debug_package %{nil}
%global __strip /bin/true
%global _build_id_links none

Name:           foxexplorer6
Version:        %{fe_version}
Release:        1%{?dist}
Summary:        Firefox with the classic Internet Explorer 6 / Windows 98 look
License:        MPL-2.0
URL:            https://github.com/mozilla-firefox/firefox
Source0:        %{fe_tarball}
ExclusiveArch:  x86_64 aarch64
Requires:       gtk3
Requires:       hicolor-icon-theme

%description
Fox Explorer 6 is an unofficial build of Mozilla Firefox restyled to look like
Internet Explorer 6 on Windows 98, with a classic light scheme and a dark scheme.
Tabs, Firefox extensions and all modern settings work as usual. It uses its own
profile (~/.mozilla/foxexplorer6), so it can be installed next to Firefox.

%prep
%setup -q -n foxexplorer6

%build
# nothing to build: the tarball is already compiled

%install
install -d %{buildroot}%{appdir}
cp -a . %{buildroot}%{appdir}/
BIN=firefox; [ -x %{buildroot}%{appdir}/foxexplorer6 ] && BIN=foxexplorer6
install -d %{buildroot}%{_bindir}
sed -e "s|@LIBDIR@|%{appdir}|" -e "s|@BINARY@|$BIN|" foxexplorer/foxexplorer6.sh.in > %{buildroot}%{_bindir}/foxexplorer6
chmod 0755 %{buildroot}%{_bindir}/foxexplorer6
install -D -m 0644 foxexplorer/foxexplorer6.desktop %{buildroot}%{_datadir}/applications/foxexplorer6.desktop
install -D -m 0644 foxexplorer/foxexplorer6.metainfo.xml %{buildroot}%{_metainfodir}/foxexplorer6.metainfo.xml
for s in 16 22 24 32 48 64 128 256; do
  install -D -m 0644 foxexplorer/appicons/foxexplorer6-$s.png %{buildroot}%{_datadir}/icons/hicolor/${s}x${s}/apps/foxexplorer6.png
done
install -D -m 0644 foxexplorer/appicons/foxexplorer6.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/foxexplorer6.svg

%files
%license foxexplorer/LICENSE
%{appdir}
%{_bindir}/foxexplorer6
%{_datadir}/applications/foxexplorer6.desktop
%{_metainfodir}/foxexplorer6.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/foxexplorer6.*

%changelog
* Mon Oct 12 2026 Fox Explorer 6 build <noreply@example.invalid> - %{fe_version}-1
- Package Fox Explorer 6
