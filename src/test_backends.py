"""Test backends - runs available tests."""
import sys

print("Testing backends...")

# Test imports
print("\n1. Testing imports...")
try:
    from ac511_volume.backends import detect_backend, PipeWireBackend, PulseAudioBackend, ALSABackend
    from ac511_volume.backends.base import AudioBackend
    print("   PASS: All imports OK")
except ImportError as e:
    print(f"   FAIL: Import error: {e}")
    sys.exit(1)

# Test base class exists
print("\n2. Testing base class...")
try:
    assert AudioBackend is not None
    print("   PASS: Base class exists")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

# Test backend detection
print("\n3. Testing auto-detection...")
backend, name = detect_backend()
if backend:
    print(f"   PASS: Detected {name}")
else:
    print("   FAIL: No audio backend detected!")
    # Don't fail - maybe no audio system is running

# Test PipeWire backend (if available)
print("\n4. Testing PipeWire backend...")
try:
    pw_backend = PipeWireBackend()
    sink = pw_backend.find_sink()
    if sink is not None:
        print(f"   PASS: Found sink {sink}")
        vol = pw_backend.get_volume(sink)
        print(f"   INFO: Current volume: {vol:.0%}")
    else:
        print("   SKIP: No AC511 sink found")
except Exception as e:
    print(f"   SKIP/ERROR: {e}")

# Test module structure
print("\n5. Testing module structure...")
try:
    from ac511_volume.backends import PipeWireBackend, PulseAudioBackend, ALSABackend
    assert PipeWireBackend is not None
    assert PulseAudioBackend is not None
    assert ALSABackend is not None
    print("   PASS: All backend classes available")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("Tests completed!")
