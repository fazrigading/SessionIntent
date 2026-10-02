Name:           sessionintent
Version:        0.4.2
Release:        1%{?dist}
Summary:        A declarative session orchestration system for GNOME Wayland

License:        GPL-3.0-or-later
URL:            https://github.com/fazrigading/SessionIntent
Source0:        https://github.com/fazrigading/SessionIntent/archive/refs/tags/v%{version}.tar.gz
Source1:        examples/apps.example.yaml

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-pyyaml
Requires:       python3-pyyaml
Requires:       python3-gobject
Requires:       (wofi or rofi)

%description
SessionIntent is a session orchestration system for GNOME Wayland.
It allows you to switch between different "intent-based modes" (Work, Gaming, Browsing, etc.)
that automatically launch, reuse, and organize your applications across workspaces.

Features:
- Intent-based session control
- Hardware-aware mode switching (battery vs AC)
- Safe, non-destructive operation
- Git-trackable configuration
- Workspace orchestration

%prep
%autosetup -n SessionIntent-%{version}

%build
%pyproject_build_wheel

%install
%pyproject_install
%pyproject_save_files sessionintent

# Install system apps config
mkdir -p %{buildroot}%{_datadir}/sessionintent/
install -m 644 examples/apps.example.yaml %{buildroot}%{_datadir}/sessionintent/apps.yaml

# Install example config
mkdir -p %{buildroot}%{_datadir}/sessionintent/examples/
install -m 644 examples/config.example.yaml %{buildroot}%{_datadir}/sessionintent/examples/config.yaml.example

# Install man page
mkdir -p %{buildroot}%{_mandir}/man1/
install -m 644 man/sessionintent.1 %{buildroot}%{_mandir}/man1/sessionintent.1

%files -f %{pyproject_files}
%doc README.md CONTRIBUTING.md docs/
%license LICENSE
%{_bindir}/sessionintent
%{_datadir}/sessionintent/
%{_mandir}/man1/sessionintent.1*

%changelog
* Fri Oct 02 2026 Fazri Gading <fazrigading@gmail.com> - 0.4.2-1
- Scanner repair, socket window tracking, GNOME 50/51 support
* Fri Sep 18 2026 Fazri Gading <fazrigading@gmail.com> - 0.3.3-1
- Stabilize: single version source, provider-plan baseline
* Tue Feb 24 2026 Fazri Gading <fazrigading@gmail.com> - 0.2.0-1
- Initial release
