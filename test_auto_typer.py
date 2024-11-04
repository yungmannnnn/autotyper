import time
from auto_typer import AutoTyper

def status_callback(status):
    print(f"Status: {status}")

def progress_callback(current, total):
    percent = (current / total) * 100
    print(f"Progress: {percent:.1f}%")

def test_auto_typer():
    print("Starting AutoTyper test...")
    typer = AutoTyper()
    
    # Test text with various patterns
    test_text = """This is a test of the optimized AutoTyper.
It should handle punctuation, like commas, and periods.
It also includes common letter pairs: there, then, in!
Testing multiple lines and typing patterns."""

    # Configure AutoTyper
    typer.set_text(test_text)
    typer.set_wpm(60)  # Moderate typing speed
    typer.set_random_delay(True, 50, 150)  # Add some natural variation
    typer.set_status_callback(status_callback)
    typer.set_progress_callback(progress_callback)

    # Start typing
    print("\nStarting typing test in 3 seconds...")
    time.sleep(3)
    
    typer.start()

    # Let it type for a few seconds
    time.sleep(5)
    
    # Test pause functionality
    print("\nTesting pause...")
    typer.toggle_pause()
    time.sleep(2)
    
    # Resume typing
    print("\nResuming typing...")
    typer.toggle_pause()
    
    # Wait for completion
    while typer.is_running():
        time.sleep(0.1)

    print("\nTest completed!")

if __name__ == "__main__":
    test_auto_typer()
