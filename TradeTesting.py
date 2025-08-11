def main():
    print("Input test: Enter spins or 'quit'")
    while True:
        inp = input("Enter spin or command: ").strip()
        if inp.lower() == "quit":
            print("Exiting.")
            break
        print(f"Received input: {inp}")
