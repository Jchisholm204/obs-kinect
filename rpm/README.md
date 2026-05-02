# obs-studio-plugin-kinect

# Issues

## Crashing on repeat launches
This is an OpenGL issue tied to libfreenect2.
Current fix is to unplug and replug the sensor.
Future fix is to update libfreenect2 to use the opencl driver rather than opengl.
Other possible options include:
- Changing `obs-kinect-freenect2/Freenect2Plugin.cpp:40` to use the CPU packet pipeline
- Releasing a CUDA specific version.
