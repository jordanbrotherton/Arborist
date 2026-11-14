Name:           arborist
Version:        1.0.0
Release:        1%{?dist}
Summary:        GTK-based GUI for atomic deployment management tools such as rpm-ostree
License:        GPL-3.0-or-later
URL:            https://github.com/jordanbrotherton/arborist
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  python3-devel
BuildRequires:  python3-rpm-macros
BuildRequires:  gtk4-devel
BuildRequires:  libadwaita-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires:       python3
Requires:       python3-gobject
Requires:       python3-dbus-fast
Requires:       gtk4
Requires:       libadwaita
Requires:       rpm-ostree

%description
Arborist is a graphical utility to manage an atomic system.
It provides an easy to use interface to help visualize and perform atomic transactions.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install
%py3_shebang_fix %{buildroot}%{_bindir}/arborist
%find_lang %{name} || true

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/io.github.jordanbrotherton.arborist.desktop || true
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/*.metainfo.xml || true
glib-compile-schemas --strict --dry-run %{buildroot}%{_datadir}/glib-2.0/schemas

%files
%license LICENSE
%doc README.md
%{_bindir}/arborist
%{_datadir}/arborist/
%{_datadir}/applications/io.github.jordanbrotherton.arborist.desktop
%{_datadir}/dbus-1/services/io.github.jordanbrotherton.arborist.service
%{_datadir}/glib-2.0/schemas/io.github.jordanbrotherton.arborist.gschema.xml
%{_datadir}/icons/hicolor/scalable/apps/io.github.jordanbrotherton.arborist.svg
%{_datadir}/icons/hicolor/symbolic/apps/io.github.jordanbrotherton.arborist-symbolic.svg
%{_datadir}/metainfo/*.metainfo.xml

%changelog
* Sat Nov 14 2026 Jordan Brotherton <jordanjbrotherton@proton.me> - 1.0.0-1
- Initial v1.0.0 RPM release
