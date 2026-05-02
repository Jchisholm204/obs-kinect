#!/usr/bin/env zsh

export OBS_KINECT_ROOT=$(git rev-parse --show-toplevel)

function setup_build_root() {
	# Setup the RPM root build directory
	local BUILDROOT_DIRS=("BUILD" "BUILDROOT" "RPMS" "SOURCES" "SPECS" "SRPMS")
	local BUILDROOT="build"

	if [[ ! -d "$BUILDROOT" ]]; then
		echo "Setting up build folder ./$BUILDROOT"
		mkdir $BUILDROOT
	fi

	for DIR in $BUILDROOT_DIRS; do
		if [[ ! -d "$BUILDROOT/$DIR" ]]; then
			echo "Creating Build Directory $BUILDROOT/$DIR"
			mkdir "$BUILDROOT/$DIR"
		fi
	done
	echo "Finished setting up RPM source directory"
}

function setup_sources() {
	local OBS_KINECT_VERSION=$1
	local FREENECT_VERSION=$2
	if [[ ! $FREENECT_VERSION ]]; then
		local FREENECT_VERSION='v0.2.1'
	fi
	tar --exclude="./rpm" \
		--transform "s|^|obs-kinect-${OBS_KINECT_VERSION}/|" \
		-czf "${OBS_KINECT_ROOT}/rpm/build/SOURCES/obs-kinect-${OBS_KINECT_VERSION}.tar.gz" \
		-C "$OBS_KINECT_ROOT" .
	wget \
		"https://github.com/OpenKinect/libfreenect2/archive/refs/tags/${FREENECT_VERSION}.tar.gz" \
		-O "${OBS_KINECT_ROOT}/rpm/build/SOURCES/${FREENECT_VERSION}.tar.gz"
}

function build_rpm() {
	rpmbuild -bb --noclean "${OBS_KINECT_ROOT}/rpm/obs-kinect.spec" \
		--define "_topdir ${OBS_KINECT_ROOT}/rpm/build"
}

setup_build_root
setup_sources '0.3.0' 'v0.2.1'
build_rpm
