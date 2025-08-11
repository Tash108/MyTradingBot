from collections import Counter, defaultdict, deque

wheel_sequence = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34,
    6, 27, 13, 36, 11, 30, 8, 23, 10, 5,
    24, 16, 33, 1, 20, 14, 31, 9, 22, 18,
    29, 7, 28, 12, 35, 3, 26
]

# Define wheel zones (8 zones roughly grouping 4-5 numbers each)
wheel_zones = [
    {0, 32, 15, 19, 4},       # Zone 1
    {21, 2, 25, 17, 34},      # Zone 2
    {6, 27, 13, 36, 11},      # Zone 3
    {30, 8, 23, 10, 5},       # Zone 4
    {24, 16, 33, 1, 20},      # Zone 5
    {14, 31, 9, 22, 18},      # Zone 6
    {29, 7, 28, 12, 35},      # Zone 7
    {3, 26}                   # Zone 8
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
    # Alternate spin directions: odd=clockwise, even=anticlockwise
    return "clockwise" if spin_number % 2 == 1 else "anticlockwise"

def get_color(number):
    red_numbers = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    black_numbers = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
    if number == 0:
        return "green"
    elif number in red_numbers:
        return "red"
    elif number in black_numbers:
        return "black"
    else:
        return "unknown"

def find_zone(number):
    for idx, zone in enumerate(wheel_zones, 1):
        if number in zone:
            return idx
    return None

class RoulettePredictor:
    def __init__(self, max_history=200, decay=0.9):
        self.spins = []  # list of tuples: (number, dealer)
        self.max_history = max_history
        self.decay = decay  # recent spins weighted more
        
        # Distance counts by spin direction with weighted counts
        self.distance_freq = {"clockwise": Counter(), "anticlockwise": Counter()}
        
        # Overall hot numbers and colors (with weighted frequencies)
        self.number_weights = Counter()
        self.color_weights = Counter()
        
        # Zone frequency overall and per dealer
        self.zone_weights = Counter()
        self.dealer_zone_weights = defaultdict(Counter)
        
        # Store spins for weighted decay processing
        self.spin_history = deque(maxlen=max_history)

    def _apply_decay(self):
        # Decay all weighted counts by decay factor
        for d in self.distance_freq:
            for dist in list(self.distance_freq[d]):
                self.distance_freq[d][dist] *= self.decay
                if self.distance_freq[d][dist] < 1e-6:
                    del self.distance_freq[d][dist]

        for num in list(self.number_weights):
            self.number_weights[num] *= self.decay
            if self.number_weights[num] < 1e-6:
                del self.number_weights[num]

        for color in list(self.color_weights):
            self.color_weights[color] *= self.decay
            if self.color_weights[color] < 1e-6:
                del self.color_weights[color]

        for zone in list(self.zone_weights):
            self.zone_weights[zone] *= self.decay
            if self.zone_weights[zone] < 1e-6:
                del self.zone_weights[zone]

        for dealer in list(self.dealer_zone_weights):
            for zone in list(self.dealer_zone_weights[dealer]):
                self.dealer_zone_weights[dealer][zone] *= self.decay
                if self.dealer_zone_weights[dealer][zone] < 1e-6:
                    del self.dealer_zone_weights[dealer][zone]
            if not self.dealer_zone_weights[dealer]:
                del self.dealer_zone_weights[dealer]

    def add_spin(self, number, dealer=None):
        # Apply decay on every new spin
        self._apply_decay()

        spin_number = len(self.spins) + 1
        self.spins.append((number, dealer))
        self.spin_history.append((number, dealer))

        # Update weighted hot numbers & colors
        self.number_weights[number] += 1
        color = get_color(number)
        self.color_weights[color] += 1

        # Update zones
        zone = find_zone(number)
        if zone:
            self.zone_weights[zone] += 1
            if dealer:
                self.dealer_zone_weights[dealer][zone] += 1

        # Update distance frequencies for spins after first spin
        if len(self.spins) > 1:
            prev_num, prev_dealer = self.spins[-2]
            direction = get_spin_direction(spin_number)
            if direction == "clockwise":
                dist = distance_clockwise(prev_num, number)
            else:
                dist = distance_anticlockwise(prev_num, number)
            self.distance_freq[direction][dist] += 1

    def predict_next_top_n(self, n=15, dealer=None):
        spin_number = len(self.spins) + 1
        direction = get_spin_direction(spin_number)

        if not self.spins:
            return "No spins recorded yet."

        if not self.distance_freq[direction]:
            return f"No distance data for spin direction '{direction}'."

        total_dist_counts = sum(self.distance_freq[direction].values())
        last_number, last_dealer = self.spins[-1]
        last_index = index_on_wheel(last_number)

        # Distance-based prediction top N
        common_distances = self.distance_freq[direction].most_common(n)
        dist_predictions = []
        for dist, count in common_distances:
            prob = count / total_dist_counts
            if direction == "clockwise":
                predicted_index = (last_index + dist) % len(wheel_sequence)
            else:
                predicted_index = (last_index - dist) % len(wheel_sequence)
            predicted_number = wheel_sequence[predicted_index]
            dist_predictions.append((predicted_number, dist, prob))

        # Hot numbers top 10 weighted
        hot_numbers_total = sum(self.number_weights.values())
        hot_numbers = self.number_weights.most_common(10)

        # Hot colors
        total_colors = sum(self.color_weights.values())
        hot_colors = [(color, count / total_colors) for color, count in self.color_weights.items()]

        # Hot zones overall top 5
        total_zones = sum(self.zone_weights.values())
        hot_zones = self.zone_weights.most_common(5)

        # Hot zones by dealer (if dealer specified)
        dealer_zone_info = None
        if dealer and dealer in self.dealer_zone_weights:
            dealer_total = sum(self.dealer_zone_weights[dealer].values())
            dealer_zone_info = self.dealer_zone_weights[dealer].most_common(5)
        elif dealer:
            dealer_zone_info = []

        # Build output string
        output = [f"Spin #{spin_number} Prediction (spin direction: {direction})"]

        output.append("\nTop distance-based predictions:")
        for num, dist, prob in dist_predictions:
            output.append(f"  Number {num} (distance {dist} steps) - probability {prob:.2%}")

        output.append("\nTop hot numbers (weighted):")
        for num, count in hot_numbers:
            prob = count / hot_numbers_total
            output.append(f"  Number {num} - weighted freq {count:.2f} ({prob:.2%})")

        output.append("\nColor distribution (weighted):")
        for color, prob in hot_colors:
            output.append(f"  {color.capitalize()} - {prob:.2%}")

        output.append("\nTop hot zones overall:")
        for zone, count in hot_zones:
            prob = count / total_zones
            output.append(f"  Zone {zone} - weighted freq {count:.2f} ({prob:.2%})")

        if dealer is not None:
            output.append(f"\nTop hot zones for dealer '{dealer}':")
            if dealer_zone_info:
                for zone, count in dealer_zone_info:
                    prob = count / sum(c for _, c in dealer_zone_info)
                    output.append(f"  Zone {zone} - weighted freq {count:.2f} ({prob:.2%})")
            else:
                output.append("  No data for this dealer yet.")

        return "\n".join(output)

def main():
    predictor = RoulettePredictor()

    print("Advanced Roulette Predictor")
    print("Enter spins in the format: <number> [dealer_name]")
    print("Example: 17 dealer1")
    print("Commands:")
    print("  predict               : Show prediction for next spin")
    print("  predict dealer <name> : Show prediction for next spin for dealer")
    print("  quit                  : Exit program")

    while True:
        inp = input("Enter spin or command: ").strip()
        if not inp:
            continue

        parts = inp.split()
        command = parts[0].lower()

        if command == "quit":
            print("Goodbye!")
            break
        elif command == "predict":
            dealer = None
            if len(parts) == 3 and parts[1].lower() == "dealer":
                dealer = parts[2]
            print(predictor.predict_next_top_n(dealer=dealer))
        else:
            # parse spin input: number and optional dealer name
            try:
                number = int(parts[0])
                if number < 0 or number > 36:
                    print("Invalid number. Must be 0-36.")
                    continue
                dealer = parts[1] if len(parts) > 1 else None
                predictor.add_spin(number, dealer)
                print(f"Recorded spin #{len(predictor.spins)}: Number {number} Dealer {dealer}")
            except ValueError:
                print("Invalid input. Enter a number (0-36) and optional dealer name, or a command.")

if __name__ == "__main__":
    main()
