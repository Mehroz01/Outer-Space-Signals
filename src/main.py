# write your code here

#"test"

def load_signal(filename: str = "signal.txt") -> str:
    """Load the 64KB signal file containing the encrypted message."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found!")
        return ""


def main():
    """Main function to run the program."""
    print("🛸 NASA Signal Decoder - Deciphering Messages from Planet Dyslexia 🛸")
    print("=" * 70)
    # Your code logic goes here -- feel free to add functions or classes as needed

    print("📡 Loading signal data...")
    signal_data = load_signal("signal.txt")
    print(signal_data)

    if not signal_data:
            return

    print("Analyzing 64KB of alien signals...")
    print("Searching for 721-character encrypted message...")


if __name__ == "__main__":
    main() 