%global debug_package %{nil}
%global repo_name obs-kinect
%global freenect_tag v0.2.1

Name:           obs-studio-plugin-kinect
Version:        0.3.0
Release:        1%{?dist}
Summary:        OBS Plugin to use a Kinect in OBS and setup a virtual green screen based on depth.
Group:          Sound and Video
License:        GPLv2
URL:            https://github.com/Jchisholm204/obs-kinect
Source0:        %{repo_name}-%{version}.tar.gz
Source1:        https://github.com/OpenKinect/libfreenect2/archive/refs/tags/%{freenect_tag}.tar.gz

BuildArch:      x86_64
Requires:       obs-studio
BuildRequires:  obs-studio-devel
BuildRequires:  xmake
BuildRequires:  gcc-c++
BuildRequires:  chrpath
# FreeNect2 Requirements
BuildRequires:  libusb1-devel
BuildRequires: 	turbojpeg-devel
BuildRequires: 	glfw-devel
Requires:       libusb1
Requires: 		turbojpeg
Requires: 		glfw

Provides:       obs-studio-plugin-kinect = %{version}
Provides: 		bundled(libfreenect2) = %{freenect_tag}

%description
OBS Plugin to access Kinect data (and setup a virtual green screen based on depth).
Bundles libfreenect2.
This repository is a fork of SirLynix/obs-kinect. Within this repository I have made modifications to:
- Remove support for the Xbox 360 Kinect
- Fixed minor build issues present on Fedora 40
- Packaged the project into an RPM (see releases page)

%prep
%setup -q -n %{repo_name}-%{version}
%setup -q -T -D -a 1 -n %{repo_name}-%{version}

%build
# FreeNect2
cd libfreenect2-0.2.1
mkdir build && cd build
cmake .. \
	-DCMAKE_INSTALL_PREFIX=../../freenect_dist \
	-DBUILD_OPENNI2_DRIVER=OFF \
	-Wno-dev \
	-DBUILD_EXAMPLES=OFF \
	-DENABLE_OPENCL=OFF \
	-DENABLE_OPENGL=ON \
	-DENABLE_CUDA=OFF \
	-DENABLE_LIBUSB=ON \
	-DCMAKE_BUILD_TYPE=Debug

%make_build
make install
cd ../..

export CPATH=$CPATH:$(pwd)/freenect_dist/include
export LIBRARY_PATH=$LIBRARY_PATH:$(pwd)/freenect_dist/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/freenect_dist/lib

# obs-kinect
xmake f -c -P .
xmake -P . -y
# Strip insecure RPATHs from the compiled binaries
chrpath --delete bin/linux_x86_64_release/*.so

%install
# Install obs-kinect
install -D -m 0755 bin/linux_x86_64_release/obs-kinect.so %{buildroot}%{_libdir}/obs-plugins/obs-kinect.so
install -D -m 0755 bin/linux_x86_64_release/libobs-kinectcore.so %{buildroot}%{_libdir}/libobs-kinectcore.so
install -D -m 0755 bin/linux_x86_64_release/obs-kinect-freenect2.so %{buildroot}%{_libdir}/obs-kinect-freenect2.so

# Install shaders/obs-kinect data
mkdir -p %{buildroot}%{_datadir}/obs/obs-plugins/obs-kinect
cp -r data/obs-plugins/obs-kinect/* %{buildroot}%{_datadir}/obs/obs-plugins/obs-kinect/

# Install the udev rule to handle the MediaTek driver conflict
install -D -m 0644 90-kinect.rules %{buildroot}%{_udevrulesdir}/90-kinect.rules

# Install FreeNect2
install -D -m 0755 freenect_dist/lib/libfreenect2.so.0.2.0 %{buildroot}%{_libdir}/libfreenect2.so.0.2.0
ln -s libfreenect2.so.0.2.0 %{buildroot}%{_libdir}/libfreenect2.so.0.2
ln -s libfreenect2.so.0.2 %{buildroot}%{_libdir}/libfreenect2.so

mkdir -p %{buildroot}%{_libdir}/pkgconfig
cp freenect_dist/lib/pkgconfig/freenect2.pc %{buildroot}%{_libdir}/pkgconfig/freenect2.pc
sed -i "s|^prefix=.*|prefix=/usr|" %{buildroot}%{_libdir}/pkgconfig/freenect2.pc
sed -i "s|^exec_prefix=.*|exec_prefix=/usr|" %{buildroot}%{_libdir}/pkgconfig/freenect2.pc
sed -i "s|^libdir=.*|libdir=%{_libdir}|" %{buildroot}%{_libdir}/pkgconfig/freenect2.pc
sed -i "s|^includedir=.*|includedir=%{_includedir}|" %{buildroot}%{_libdir}/pkgconfig/freenect2.pc

mkdir -p %{buildroot}%{_includedir}/libfreenect2
cp -r freenect_dist/include/libfreenect2/* %{buildroot}%{_includedir}/libfreenect2/

%post
# Fix ldconfig
/sbin/ldconfig
# Reload USB device rules
/usr/bin/udevadm control --reload-rules
/usr/bin/udevadm trigger

%postun -p /sbin/ldconfig

%files
%license LICENSE
%doc README.md
# obs-kinect
%{_libdir}/obs-plugins/obs-kinect.so
%{_libdir}/libobs-kinectcore.so
%{_libdir}/obs-kinect-freenect2.so
%{_datadir}/obs/obs-plugins/obs-kinect/
%{_udevrulesdir}/90-kinect.rules
# freenect
%{_libdir}/libfreenect2.so
%{_libdir}/libfreenect2.so.0.2
%{_libdir}/libfreenect2.so.0.2.0
%{_libdir}/pkgconfig/freenect2.pc
%{_includedir}/libfreenect2/


%changelog
* Fri May 1 2026 Jacob Chisholm <jacob@example.com> - 0.3.0-1
- Initial creation of the RPM package
- Targeted for Fedora 40 and AlmaLinux 10
