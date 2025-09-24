#!/usr/bin/env python3
"""
Test script for text-to-speech functionality
"""

def test_tts_simple():
    """Test basic text-to-speech using system commands"""
    import subprocess
    import sys

    test_text = "Hello, this is a test of the text to speech system!"

    print("Testing text-to-speech...")
    print(f"Text: {test_text}")

    # Try different TTS methods available on Linux
    methods = [
        # espeak - simple and widely available
        ["espeak", test_text],
        # festival - another common TTS engine
        ["echo", test_text, "|", "festival", "--tts"],
        # spd-say - speech dispatcher
        ["spd-say", test_text]
    ]

    for i, method in enumerate(methods):
        print(f"\nTrying method {i+1}: {' '.join(method[:2])}")
        try:
            if "|" in method:
                # Handle piped commands
                p1 = subprocess.Popen(["echo", test_text], stdout=subprocess.PIPE)
                p2 = subprocess.Popen(["festival", "--tts"], stdin=p1.stdout)
                p1.stdout.close()
                p2.wait()
            else:
                subprocess.run(method, check=True, timeout=10)
            print("✓ Success!")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"✗ Failed: {e}")

    print("\nNo TTS methods worked. You may need to install:")
    print("  sudo apt install espeak")
    print("  or")
    print("  sudo apt install festival")
    print("  or")
    print("  sudo apt install speech-dispatcher")
    return False

def test_tts_pyttsx3():
    """Test pyttsx3 library if available"""
    try:
        import pyttsx3
        print("\nTesting pyttsx3...")

        engine = pyttsx3.init()
        test_text = "Pyttsx3 text to speech is working!"
        print(f"Text: {test_text}")

        engine.say(test_text)
        engine.runAndWait()
        print("✓ pyttsx3 success!")
        return True

    except ImportError:
        print("\n✗ pyttsx3 not available")
        print("Install with: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"\n✗ pyttsx3 error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TEXT-TO-SPEECH TEST")
    print("=" * 50)

    # Test system TTS
    system_works = test_tts_simple()

    # Test pyttsx3
    pyttsx3_works = test_tts_pyttsx3()

    print("\n" + "=" * 50)
    print("RESULTS:")
    print(f"System TTS: {'✓ Working' if system_works else '✗ Not working'}")
    print(f"pyttsx3:    {'✓ Working' if pyttsx3_works else '✗ Not working'}")

    if not system_works and not pyttsx3_works:
        print("\nNo TTS methods are working!")
        print("Recommendations:")
        print("1. Install espeak: sudo apt install espeak")
        print("2. Or install festival: sudo apt install festival")
        print("3. Test audio: speaker-test -t sine -f 1000 -l 1")
    else:
        print("\nAt least one TTS method is working!")