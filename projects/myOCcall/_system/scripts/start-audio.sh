#!/bin/bash
# Avvia PulseAudio headless con virtual sink per cattura call
if pgrep -x pulseaudio > /dev/null; then
    echo "PulseAudio already running (PID: $(pgrep pulseaudio))"
    exit 0
fi

rm -f /run/user/$(id -u)/pulse/native /run/user/$(id -u)/pulse/pid 2>/dev/null
pulseaudio --daemonize=yes --exit-idle-time=-1
sleep 2

if pactl info > /dev/null 2>&1; then
    echo "PulseAudio started OK"
    pactl list short sinks
else
    echo "ERROR: PulseAudio failed to start"
    exit 1
fi
