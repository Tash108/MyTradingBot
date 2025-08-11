from collections import Counter

wheel_sequence = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34,
    6, 27, 13, 36, 11, 30, 8, 23, 10, 5,
    24, 16, 33, 1, 20, 14, 31, 9, 22, 18,
    29, 7, 28, 12, 35, 3, 26
]

def index_on_wheel(number):
    return wheel_sequence.index(number)

def distance_clockwise(from_num, to_num):
    from_idx = index_on_wheel(from_num)
    to_idx = index_on_wheel(to_num)
    return (to_idx - from_idx) % len(wheel_sequence)

def distance_anticlockwise(from_num, to_num):
    from_idx = index_on_wheel(from_num)
    to_idx = index_on_wheel(to_num)
    return (from_idx - to_idx) % len(wheel_sequence)

def get_spin_direction(spin_number):
    return "clockwise" if spin_number % 2 == 1 else "anticlockwise"

class RoulettePredictor:
    def __init__(self):
        self.spins = []
        self.distance_freq = {"clockwise": Counter(), "anticlockwise": Counter()}

    def add_spin(self, number):
        spin_number = len(self.spins) + 1
        self.spins.append(number)

        if len(self.spins) > 1:
            prev_num = self.spins[-2]
            direction = get_spin_direction(spin_number)
            if direction == "clockwise":
                dist = distance_clockwise(prev_num, number)
            else:
                dist = distance_anticlockwise(prev_num, number)
            self.distance_freq[direction][dist] += 1

    def predict_next_top_n(self, n=15):
        spin_number = len(self.spins) + 1
        direction = get_spin_direction(spin_number)

        if not self.spins:
            return "No spins recorded yet."

        if not self.distance_freq[direction]:
            return f"No distance data for spin direction '{direction}'."

        total_counts = sum(self.distance_freq[direction].values())
        last_number = self.spins[-1]
        last_index = index_on_wheel(last_number)

        # Get the n most common distances and their counts
        common_distances = self.distance_freq[direction].most_common(n)

        results = []
        for dist, count in common_distances:
            prob = count / total_counts
            if direction == "clockwise":
                predicted_index = (last_index + dist) % len(wheel_sequence)
            else:
                predicted_index = (last_index - dist) % len(wheel_sequence)
            predicted_number = wheel_sequence[predicted_index]
            results.append((predicted_number, dist, prob))

        output = [
            f"Spin #{spin_number} (direction: {direction}): Top {n} likely next numbers:"
        ]
        for num, dist, prob in results:
            output.append(f"  Number {num} at distance {dist} steps — probability: {prob:.2%}")

        return "\n".join(output)

def main():
    predictor = RoulettePredictor()

    print("Roulette live spin predictor (top N predictions)")
    print("Enter spin numbers (0-36). Type 'predict' to get next spin prediction, 'quit' to exit.")

    while True:
        user_input = input("Enter spin or command: ").strip().lower()
        if user_input == "quit":
            print("Exiting.")
            break
        elif user_input == "predict":
            print(predictor.predict_next_top_n(15))
        else:
            try:
                num = int(user_input)
                if 0 <= num <= 36:
                    predictor.add_spin(num)
                    print(f"Recorded spin #{len(predictor.spins)}: {num}")
                else:
                    print("Invalid number. Must be 0-36.")
            except ValueError:
                print("Invalid input. Enter a number, 'predict', or 'quit'.")

if __name__ == "__main__":
    main()
