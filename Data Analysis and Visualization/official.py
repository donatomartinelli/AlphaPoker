import random
from collections import Counter, defaultdict
from colorama import Fore, Style, init
from itertools import combinations
import matplotlib.pyplot as plt

# Initialize colorama for colored terminal output
init(autoreset=True)


def create_deck():
    """
    Creates a standard 52-card deck with colored suit symbols.
    
    Returns:
        tuple: (list of card tuples, dict of suits with color codes)
    """
    suits = {'♥': Fore.RED,'♦': Fore.RED,'♣': Fore.BLACK,'♠': Fore.BLACK}
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [(value, suit) for suit in suits.keys() for value in values]
    return deck, suits

def card_value(card):
    """
    Converts card face value to numeric value for comparison.
    
    Args:
        card (tuple): A card in (value, suit) format
        
    Returns:
        int: Numeric value of the card (2-14, with Ace high)
    """
    value, _ = card
    if value.isdigit():
        return int(value)
    elif value == 'J':
        return 11
    elif value == 'Q':
        return 12
    elif value == 'K':
        return 13
    elif value == 'A':
        return 14

def translate_suit(suit_text):
    """
    Translate written suit names to symbols.
    
    Args:
        suit_text (str): Text representation of a suit (e.g., 'h', 'hearts')
        
    Returns:
        str: Unicode symbol for the suit
    """
    suit_mapping = {'h': '♥','d': '♦','c': '♣','s': '♠'}
    return suit_mapping.get(suit_text.lower())

def parse_card_input(card_str, deck):
    """
    Parse a card string with written suit names and validate if it exists in the deck.
    
    Args:
        card_str (str): User input string like "A hearts" or "10 s"
        deck (list): Current deck of cards
        
    Returns:
        tuple: Valid card in (value, suit) format
        
    Raises:
        ValueError: If input format is invalid or card is not in deck
    """
    try:
        parts = card_str.strip().split()
        if len(parts) < 2:
            raise ValueError("Invalid input format")
            
        value = parts[0].upper()
        # Join the remaining parts in case the suit name has spaces
        suit_text = ' '.join(parts[1:])
        suit = translate_suit(suit_text)
        
        if suit is None:
            raise ValueError("Invalid suit. Use hearts/h, diamonds/d, clubs/c, or spades/s")
            
        if value not in ['2','3','4','5','6','7','8','9','10','J','Q','K','A']:
            raise ValueError("Invalid card value")
            
        card = (value, suit)
        if card not in deck:
            raise ValueError("Card not in deck")
            
        return card
    except ValueError as e:
        if str(e) == "Card not in deck":
            raise ValueError("Card not in deck or already used")
        raise ValueError(str(e)) 

def pick_random_cards(deck, n):
    """
    Pick n random cards from the deck.
    
    Args:
        deck (list): Deck of cards
        n (int): Number of cards to pick
        
    Returns:
        list: n randomly selected cards
    """
    random.shuffle(deck)
    picked_cards = [deck.pop() for _ in range(n)]
    return picked_cards

def order_hand_by_rank(hand):
    """
    Orders cards in a poker hand according to poker hand display rules:
    - Groups (four of a kind, three of a kind, pairs) come first
    - Highest groups come first
    - Remaining cards (kickers) are ordered by rank
    
    Args:
        hand (list): List of card tuples
        
    Returns:
        list: Ordered cards for display
    """
    values = [card_value(card) for card in hand]
    value_counts = Counter(values)
    
    # Create a list of tuples (card, value_count, card_value)
    card_info = [(card, value_counts[card_value(card)], card_value(card)) for card in hand]
    
    # Sort by:
    # 1. Count of cards (4 of a kind > 3 of a kind > pair > single)
    # 2. Card value within same count (higher value pairs come before lower value pairs)
    # 3. For single cards (kickers), sort by value
    sorted_cards = sorted(card_info, 
                         key=lambda x: (x[1], x[2]), 
                         reverse=True)
    
    return [card[0] for card in sorted_cards]

def format_cards(cards, suits):
    """
    Format cards for colored terminal display, properly ordered by poker hand rules.
    
    Args:
        cards (list): List of card tuples
        suits (dict): Dictionary mapping suit symbols to color codes
        
    Returns:
        str: Formatted string of cards with colors
    """
    ordered_cards = order_hand_by_rank(cards)
    return ' '.join(f"{suits[suit]}{value} {suit}{Style.RESET_ALL}" 
                   for value, suit in ordered_cards)

def count_hole_cards_used(hole_cards, best_hand):
    """
    Count how many cards from the hole cards are used in the best hand.
    
    Args:
        hole_cards (list): Player's hole cards
        best_hand (list): Best 5-card hand
        
    Returns:
        int: Number of hole cards used (0, 1, or 2)
    """
    hole_card_set = set(hole_cards)
    best_hand_set = set(best_hand)
    return len(hole_card_set.intersection(best_hand_set))

def identify_hand_ranking(hand):
    """
    Identifies the poker hand ranking and creates a detailed ranking tuple.
    
    Args:
        hand (list): 5-card hand
        
    Returns:
        tuple: (hand_type_rank, detailed_ranking_tuple)
            - hand_type_rank is 1-10 (1=High Card, 10=Royal Flush)
            - detailed_ranking_tuple contains values for tiebreakers
    """
    values = sorted([card_value(card) for card in hand], reverse=True)
    suits = [card[1] for card in hand]
    suit_counts = Counter(suits)
    value_counts = Counter(values)
    
    # Get groups sorted by size then value
    groups = sorted(((count, val) for val, count in value_counts.items()),
                   key=lambda x: (-x[0], -x[1]))
    
    # Helper function to create detailed ranking for tiebreakers
    def get_detailed_ranking(include_suits=False):
        # First element is hand type rank (1-10)
        # Subsequent elements are card values in order of importance for breaking ties
        ranking = []
        
        # Add all groups in order of size
        for count, value in groups:
            ranking.append(value)
            
        # For hands without enough groups to compare (like flushes), 
        # add remaining cards in descending order
        while len(ranking) < 5:
            remaining = [v for v in values if v not in ranking]
            if remaining:
                ranking.append(remaining[0])
            else:
                break
        
        # For flush-based hands, include suit information
        if include_suits:
            ranking.append(suits[0])  # All cards will have same suit
            
        return tuple(ranking)

    # Check for hand types
    is_flush = len(suit_counts) == 1
    is_straight = len(value_counts) == 5 and (values[0] - values[4] == 4)
    
    # Return tuple with hand type rank and detailed ranking for tiebreakers
    # Hand type ranks: 10=Royal Flush, 9=Straight Flush, 8=Four of a Kind, etc.
    if is_flush and is_straight:
        if values[0] == 14:  # Ace high
            return (10, (14, 13, 12, 11, 10, suits[0]))  # Royal Flush
        return (9, get_detailed_ranking(include_suits=True))  # Straight Flush
    
    if 4 in value_counts.values():
        return (8, get_detailed_ranking())  # Four of a Kind
        
    if 3 in value_counts.values() and 2 in value_counts.values():
        return (7, get_detailed_ranking())  # Full House
        
    if is_flush:
        return (6, get_detailed_ranking(include_suits=True))  # Flush
        
    if is_straight:
        return (5, get_detailed_ranking())  # Straight
        
    if 3 in value_counts.values():
        return (4, get_detailed_ranking())  # Three of a Kind
        
    if list(value_counts.values()).count(2) == 2:
        return (3, get_detailed_ranking())  # Two Pair
        
    if 2 in value_counts.values():
        return (2, get_detailed_ranking())  # One Pair
        
    return (1, get_detailed_ranking())  # High Card

def format_best_hand(rank, suits):
    """
    Formats the hand ranking name for display.
    
    Args:
        rank (tuple): Hand ranking tuple from identify_hand_ranking
        suits (dict): Dictionary of suits with color codes
        
    Returns:
        str: Human-readable hand ranking name
    """
    rank_value = rank[0]

    if rank_value == 10:
        return "Royal Flush "
    elif rank_value == 9:
        return "Straight Flush "
    elif rank_value == 8:
        return f"Four of a Kind "
    elif rank_value == 7:
        return f"Full House "
    elif rank_value == 6:
        return "Flush "
    elif rank_value == 5:
        return "Straight "
    elif rank_value == 4:
        return f"Three of a Kind "
    elif rank_value == 3:
        return f"Two Pair "
    elif rank_value == 2:
        return f"One Pair "
    else:
        return "High Card "

def form_hands_from_board(hole_cards, board):
    """
    Generates all possible 5-card hands from hole cards and board.
    
    Args:
        hole_cards (list): Player's 2 hole cards
        board (list): Community cards on the board
        
    Returns:
        list: All possible 5-card combinations
    """
    all_cards = hole_cards + board
    return list(combinations(all_cards, 5))

def generate_all_two_card_combinations(deck):
    """
    Generate all possible 2-card combinations from the deck.
    
    Args:
        deck (list): Current deck of cards
        
    Returns:
        list: All possible 2-card combinations
    """
    return list(combinations(deck, 2))

def get_detailed_position_stats(ranked_hands, my_position):
    """
    Get detailed statistics about hand position.
    
    Args:
        ranked_hands (list): List of ranked hand dictionaries
        my_position (str): Position of the player's hand (e.g., '1T', '3T')
    
    Returns:
        dict: Detailed position statistics
    """
    # Extract position numbers (removing the 'T' suffix and converting to int)
    my_pos_num = int(my_position[:-1])
    
    # Count ties and hands above and below
    ties_above = set()
    ties_below = set()
    hands_above = 0
    hands_below = 0
    hands_in_my_tie = 0
    
    # Analyze each hand's position
    for hand in ranked_hands:
        pos_str = hand['position']
        pos_num = int(pos_str[:-1])
        
        if pos_num < my_pos_num:
            hands_above += 1
            ties_above.add(pos_str)
        elif pos_num > my_pos_num:
            hands_below += 1
            ties_below.add(pos_str)
        else:  # Same position as mine
            hands_in_my_tie += 1
    
    # Total number of hands (N)
    total_hands = hands_above + hands_in_my_tie + hands_below
    
    return {
        'ties_above': len(ties_above),
        'hands_above': hands_above,
        'ties_below': len(ties_below),
        'hands_below': hands_below,
        'hands_in_my_tie': hands_in_my_tie,
        'total_hands': total_hands
    }

def calculate_hand_strength(position, position_counts, street='flop'):
    """
    Calculate the hand strength based on position and tie cardinality.
    
    Args:
        position (str): Position of the hand (e.g., '1T', '2T', etc.)
        position_counts (dict): Dictionary mapping positions to number of hands in that position
        street (str): Current street - 'flop', 'turn', or 'river'
    
    Returns:
        float: Hand strength score from 0 to 100
    """
    # Convert position string to integer (remove 'T' suffix)
    current_position = int(position[:-1])
    
    # Calculate total number of hands below current position
    hands_below = sum(position_counts[i] for i in range(current_position + 1, len(position_counts) + 1))
    
    # Set divisor based on street
    if street == 'turn':
        divisor = 1035
    elif street == 'river':
        divisor = 990
    else:  # default to flop
        divisor = 1081
    
    # Calculate Hand Strength as percentage of hands below your position
    hand_strength = (hands_below / divisor) * 100
    
    return round(hand_strength, 2)

def normalize_strengths(ranked_hands):
    """
    Normalize all hand strengths to a 0-100 scale.
    
    Args:
        ranked_hands (list): List of hand dictionaries with strength values
        
    Returns:
        list: Updated list with normalized strength values
    """
    # Get all strength values
    strengths = [hand['strength'] for hand in ranked_hands]
    min_strength = min(strengths)
    max_strength = max(strengths)
    
    # Normalize each hand's strength to 0-100 scale
    for hand in ranked_hands:
        if max_strength == min_strength:
            hand['strength'] = 100 if hand['strength'] == max_strength else 0
        else:
            hand['strength'] = round(((hand['strength'] - min_strength) / (max_strength - min_strength)) * 100, 2)
    
    return ranked_hands

def analyze_all_possible_hands(deck, board, my_cards, suits, street='flop'):
    """
    Analyze and rank all possible two-card combinations for a given board.
    
    Args:
        deck (list): Current deck of cards
        board (list): Community cards on the board
        my_cards (list): Player's hole cards
        suits (dict): Dictionary of suits with color codes
        street (str): Current street - 'flop', 'turn', or 'river'
        
    Returns:
        list: Ranked list of all possible hands with details
    """
    # Create a temporary deck that includes my_cards for analysis
    temp_deck = deck.copy()
    for card in my_cards:
        if card not in temp_deck:
            temp_deck.append(card)
            
    # Generate all possible 2-card combinations
    all_two_card_combinations = generate_all_two_card_combinations(temp_deck)
    hand_rankings = []
    
    # Convert my_cards to a set for easier checking
    my_cards_set = set(my_cards)
    my_cards_tuple = tuple(sorted(my_cards, key=lambda x: (card_value(x), x[1])))
    
    # Process each possible combination
    for combination in all_two_card_combinations:
        # Convert combination to set for intersection
        combo_set = set(combination)
        
        # Skip combinations that have only one card in common with my_cards
        # (these would be invalid hole card combinations)
        intersection = my_cards_set.intersection(combo_set)
        if len(intersection) == 1:  # Skip if only one card matches
            continue
            
        # Sort the combination for consistency
        sorted_combination = tuple(sorted(combination, key=lambda x: (card_value(x), x[1])))
        
        # Generate all possible 5-card hands with this combination
        possible_hands = form_hands_from_board(list(sorted_combination), board)
        
        # Find the best hand from all possibilities
        best_hand = max(possible_hands, key=lambda hand: identify_hand_ranking(hand))
        hand_rank = identify_hand_ranking(best_hand)
        
        # Count how many hole cards were used
        cards_used = count_hole_cards_used(sorted_combination, best_hand)
        
        # Add to rankings
        hand_rankings.append({
            'hole_cards': sorted_combination,
            'best_hand': best_hand,
            'rank': hand_rank,
            'cards_used': cards_used
        })
    
    # Make sure the player's cards are included in the analysis
    my_cards_in_rankings = any(
        set(hand['hole_cards']) == set(my_cards) for hand in hand_rankings
    )
    
    if not my_cards_in_rankings:
        possible_hands = form_hands_from_board(list(my_cards), board)
        best_hand = max(possible_hands, key=lambda hand: identify_hand_ranking(hand))
        hand_rank = identify_hand_ranking(best_hand)
        cards_used = count_hole_cards_used(my_cards, best_hand)
        
        hand_rankings.append({
            'hole_cards': my_cards_tuple,
            'best_hand': best_hand,
            'rank': hand_rank,
            'cards_used': cards_used
        })
    
    # Sort by hand rank (best hands first)
    hand_rankings.sort(key=lambda x: x['rank'], reverse=True)

    # Assign positions and handle ties
    current_rank = None
    current_position = 1
    position_counts = defaultdict(int)
    
    for i, hand in enumerate(hand_rankings):
        if current_rank != hand['rank']:
            current_rank = hand['rank']
            hand['position'] = f"{current_position}T"  # T indicates a place/tier
            position_counts[current_position] += 1
            current_position += 1
        else:
            # Same rank means same position (tie)
            hand['position'] = f"{current_position-1}T"
            position_counts[current_position-1] += 1
    
    # Calculate hand strength for each hand
    for hand in hand_rankings:
        hand['strength'] = calculate_hand_strength(
            hand['position'],
            position_counts,
            street
        )
    
    # Normalize strengths to 0-100 scale
    hand_rankings = normalize_strengths(hand_rankings)
    
    return hand_rankings

def display_hand_rankings(ranked_hands, suits, mode='condensed'):
    """
    Display all possible two-card combinations and their rankings.
    
    Args:
        ranked_hands (list): List of ranked hand dictionaries
        suits (dict): Dictionary of suits with color codes
        mode (str): Display mode - 'detailed' or 'condensed'
    """
    if mode.lower() == 'condensed':
        print("\nCondensed Hand Rankings (from best to worst):")
        print("-" * 80)
        print(f"{'Pos':>4} | {'Hand':^20} | {'Best Hand':<15} | {'Used':<4} | {'Strength':>8}")
        print("-" * 80)
        
        # Create a dictionary to track unique positions
        position_data = {}
        
        # Process all hands and group by position
        for hand in ranked_hands:
            position = hand['position']
            hand_type = format_best_hand(hand['rank'], suits).strip()
            cards_used = hand['cards_used']
            strength = hand['strength']
            
            # Extract card values and suits
            card1, card2 = hand['hole_cards']
            val1, suit1 = card1
            val2, suit2 = card2
            
            # Convert "10" to "T" for display (poker notation)
            if val1 == "10":
                val1 = "T"
            if val2 == "10":
                val2 = "T"
            
            # Order values (higher value first)
            if card_value(card1) < card_value(card2):
                val1, val2 = val2, val1
                suit1, suit2 = suit2, suit1
                
            # Check if suited
            is_suited = suit1 == suit2
            
            # Create a unique key for this hand type within the position
            hand_key = f"{val1}{val2}"
            
            # Initialize position if needed
            if position not in position_data:
                position_data[position] = {
                    'hand_type': hand_type,
                    'cards_used': cards_used,
                    'strength': strength,
                    'hands': {}
                }
            
            # Track suited/offsuit for this hand value combination
            if hand_key not in position_data[position]['hands']:
                position_data[position]['hands'][hand_key] = {'suited': False, 'offsuit': False}
                
            if is_suited:
                position_data[position]['hands'][hand_key]['suited'] = True
            else:
                position_data[position]['hands'][hand_key]['offsuit'] = True
        
        # Sort positions by their numeric value
        sorted_positions = sorted(position_data.keys(), key=lambda x: int(x[:-1]))
        
        # Display each position
        for position in sorted_positions:
            pos_info = position_data[position]
            hand_notations = []
            
            # Build hand notations with combined os suffix for both suited and offsuit
            for hand_key, suit_info in pos_info['hands'].items():
                if suit_info['suited'] and suit_info['offsuit']:
                    # Both suited and offsuit exist - use combined notation
                    hand_notations.append(f"{hand_key}os")
                elif suit_info['suited']:
                    hand_notations.append(f"{hand_key}s")
                else:
                    hand_notations.append(f"{hand_key}o")
            
            # Format the hand notations
            formatted_notations = ' '.join(sorted(hand_notations))
            
            print(f"{position:>4} | {formatted_notations:<20} | {pos_info['hand_type']:<15} | {pos_info['cards_used']:>4} | {pos_info['strength']:>8.2f}")
    
    else:  # detailed mode
        print("\nAll possible two-card combinations ranked (from best to worst):")
        print("-" * 120)
        print(f"{'Pos':>4} | {'Hole Cards':<20} | {'Best Hand':<15} | {'Used':<4} | {'Strength':>8} | {'Best Five Cards'}")
        print("-" * 120)
        
        for hand in ranked_hands:
            position_str = hand['position']
            hole_cards = format_cards(hand['hole_cards'], suits)
            best_hand = format_cards(hand['best_hand'], suits)
            hand_type = format_best_hand(hand['rank'], suits)
            cards_used = hand['cards_used']
            strength = hand['strength']
            
            print(f"{position_str:>4} | {hole_cards:<20} | {hand_type:<15} | {cards_used:>4} | {strength:>8.2f} | {best_hand}")

def get_position_stats(ranked_hands):
    """
    Analyzes position statistics from ranked hands.
    
    Args:
        ranked_hands (list): List of ranked hand dictionaries
    
    Returns:
        tuple: (last_position, position_counts) where:
            - last_position: integer of the highest position number
            - position_counts: dictionary of position numbers and their frequencies
    """
    # Extract position numbers (removing the 'T' suffix and converting to int)
    positions = [int(hand['position'][:-1]) for hand in ranked_hands]
    
    # Get the highest position number
    last_position = max(positions)
    
    # Count frequency of each position
    position_counts = {}
    for pos in range(1, last_position + 1):
        count = sum(1 for p in positions if p == pos)
        position_counts[pos] = count
    
    # Return both values
    return last_position, position_counts

def visualize_my_position(position_counts, my_position):
    """
    Create a bar chart highlighting only the player's position.
    
    Args:
        position_counts (dict): Dictionary of position numbers and their frequencies
        my_position (str): Position of the player's hand (e.g., '1T', '3T')
    """
    positions = list(position_counts.keys())
    counts = list(position_counts.values())
    
    plt.figure(figsize=(12, 7))
    
    # Create bars with default color
    bars = plt.bar(positions, counts, color='lightblue')
    
    # Extract the numeric position (remove 'T' suffix)
    pos_num = int(my_position[:-1])
    
    # Highlight the bar where player's hand falls
    bars[pos_num - 1].set_color('lightgreen')
    
    # Add player label above the bar
    bar = bars[pos_num - 1]
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
            'You',
            ha='center', va='bottom',
            fontsize=9, fontweight='bold')
    
    plt.title('Number of Hands per Position')
    plt.xlabel('Position')
    plt.ylabel('Number of Hands')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adjust margins to make room for labels
    plt.subplots_adjust(top=0.9)
    
    plt.show()

def count_ties(ranked_hands):
    """
    Count the number of ties in the ranked hands.
    
    Args:
        ranked_hands (list): List of ranked hands
    
    Returns:
        dict: A dictionary with tie positions and their frequencies
    """
    position_ties = defaultdict(int)
    
    # Group hands by their position
    position_groups = defaultdict(list)
    for hand in ranked_hands:
        position_groups[hand['position']].append(hand)
    
    # Count ties (groups with more than one hand)
    for position, group in position_groups.items():
        if len(group) > 1:
            position_ties[position] = len(group)
    
    return position_ties

def get_user_flop(deck):
    """
    Get 3 cards for the flop from user input.
    
    Args:
        deck (list): Current deck of cards
    
    Returns:
        list: 3 flop cards
    """
    print("\nEnter 3 cards for the flop.")
    
    flop = []
    
    for i in range(3):
        while True:
            try:
                card = parse_card_input(input(f"Enter card {i+1}: "), deck)
                deck.remove(card)  # Remove the card from the deck
                flop.append(card)
                break
            except ValueError as e:
                print(e)
    
    return flop

def analyze_turn(my_cards, flop, deck, suits, display_mode='condensed'):
    """
    Analyze hand strength after the turn card.
    
    Args:
        my_cards (list): Player's hole cards
        flop (list): Flop cards
        deck (list): Current deck
        suits (dict): Dictionary of suits with color codes
    
    Returns:
        tuple: (turn_card, updated_deck)
    """
    while True:
        turn_choice = input("\nDo you want to enter the turn card manually? (y/n): ").lower()
        if turn_choice in ['y', 'n']:
            break
        print("Please answer with 'y' or 'n'.")
    
    if turn_choice == 'y':
        # Manual turn input        
        while True:
            try:
                turn_card = parse_card_input(input("Enter turn card: "), deck)
                deck.remove(turn_card)  # Remove from deck
                break
            except ValueError as e:
                print(e)
    else:
        # Random turn generation
        temp_deck = deck.copy()
        random.shuffle(temp_deck)
        turn_card = temp_deck[0]
        deck.remove(turn_card)
    
    print("\nTurn card:")
    print(format_cards([turn_card], suits))
    
    # Create new board with turn
    board = flop + [turn_card]
    
    # Analyze all possible hands with turn - specify we're on the turn
    print("\nAnalyzing all possible combinations after turn...")
    ranked_hands = analyze_all_possible_hands(deck, board, my_cards, suits, street='turn')
    
    # Display updated rankings 
    display_hand_rankings(ranked_hands, suits, mode=display_mode)
    
    # Find your hand's position and stats
    filtered_hands = [
        hand for hand in ranked_hands 
        if set(my_cards) == set(hand['hole_cards'])
    ]
    
    # Display updated statistics
    print("\nYour Hand Statistics After Turn:")
    if filtered_hands:
        best_hand = filtered_hands[0]
        position_stats = get_detailed_position_stats(ranked_hands, best_hand['position'])

        print(f"Hole Cards: {format_cards(best_hand['hole_cards'], suits)}")
        print(f"Board: {format_cards(board, suits)}")
        print(f"Your Hand: {format_cards(best_hand['best_hand'], suits)} - {format_best_hand(best_hand['rank'], suits)} ")
        print(f"Cards Used: {best_hand['cards_used']}")
        print(f"Your Tie: {best_hand['position']} - Hands in your tie: {position_stats['hands_in_my_tie']}")
        print(f"Ties above yours: {position_stats['ties_above']} - Total hands above: {position_stats['hands_above']}")
        print(f"Ties below yours: {position_stats['ties_below']} - Total hands below: {position_stats['hands_below']}")
        print(f"Strength: {best_hand['strength']:.2f}%")
        
        # Visualize updated position distribution
        last_position, position_counts = get_position_stats(ranked_hands)
        visualize_my_position(position_counts, best_hand['position'])
    else:
        print("No valid combination found with your cards.")
    
    return turn_card, deck

def analyze_river(my_cards, flop, turn_card, deck, suits, display_mode='condensed'):
    """
    Analyze hand strength after the river card.
    
    Args:
        my_cards (list): Player's hole cards
        flop (list): Flop cards
        turn_card (tuple): Turn card
        deck (list): Current deck
        suits (dict): Dictionary of suits with color codes
    
    Returns:
        tuple: (river_card, updated_deck)
    """
    while True:
        river_choice = input("\nDo you want to enter the river card manually? (y/n): ").lower()
        if river_choice in ['y', 'n']:
            break
        print("Please answer with 'y' or 'n'.")
    
    if river_choice == 'y':
        # Manual river input
        while True:
            try:
                river_card = parse_card_input(input("Enter river card: "), deck)
                deck.remove(river_card)  # Remove from deck
                break
            except ValueError as e:
                print(e)
    else:
        # Random river generation
        temp_deck = deck.copy()
        random.shuffle(temp_deck)
        river_card = temp_deck[0]
        deck.remove(river_card)
    
    print("\nRiver card:")
    print(format_cards([river_card], suits))
    
    # Create complete board
    board = flop + [turn_card, river_card]
    
    # Analyze all possible hands with river - specify we're on the river
    print("\nAnalyzing all possible combinations after river...")
    ranked_hands = analyze_all_possible_hands(deck, board, my_cards, suits, street='river')
    
    # Display updated rankings
    display_hand_rankings(ranked_hands, suits, mode=display_mode)
    
    # Find your hand's position and stats
    filtered_hands = [
        hand for hand in ranked_hands 
        if set(my_cards) == set(hand['hole_cards'])
    ]
    
    # Display updated statistics
    print("\nYour Hand Statistics After River:")
    if filtered_hands:
        best_hand = filtered_hands[0]
        position_stats = get_detailed_position_stats(ranked_hands, best_hand['position'])

        print(f"Hole Cards: {format_cards(best_hand['hole_cards'], suits)}")
        print(f"Board: {format_cards(board, suits)}")
        print(f"Your Hand: {format_cards(best_hand['best_hand'], suits)} - {format_best_hand(best_hand['rank'], suits)} ")
        print(f"Cards Used: {best_hand['cards_used']}")
        print(f"Your Tie: {best_hand['position']} - Hands in your tie: {position_stats['hands_in_my_tie']}")
        print(f"Ties above yours: {position_stats['ties_above']} - Total hands above: {position_stats['hands_above']}")
        print(f"Ties below yours: {position_stats['ties_below']} - Total hands below: {position_stats['hands_below']}")
        print(f"Strength: {best_hand['strength']:.2f}%")
        
        # Visualize updated position distribution
        last_position, position_counts = get_position_stats(ranked_hands)
        visualize_my_position(position_counts, best_hand['position'])
    else:
        print("No valid combination found with your cards.")
    
    return river_card, deck

def main():
    print("\nPoker Hand Analysis Tool")
    print("-" * 50)
    
    # Choose display mode
    display_mode = 'condensed'  # Default
    while True:
        mode_choice = input("Choose display mode (detailed/condensed or d/c): ").lower()
        if mode_choice in ['detailed', 'condensed', 'd', 'c']:
            display_mode = 'detailed' if mode_choice in ['detailed', 'd'] else 'condensed'
            break
        print("Please choose either 'detailed' or 'condensed'.")

    # Create a single deck
    deck, suits = create_deck()
    
    # Get user's cards (manual input or random)
    while True:
        choice = input("Do you want to enter your cards manually? (y/n): ").lower()
        if choice in ['y', 'n']:
            break
        print("Please answer with 'y' or 'n'.")
    
    if choice == 'y':
        # Manual card input
        print("\nEnter your two cards.")
        while True:
            try:
                card1 = parse_card_input(input("Enter card 1: "), deck)
                card2 = parse_card_input(input("Enter card 2: "), deck)
                my_cards = [card1, card2]
                # Validate that cards are different
                if card1 == card2:
                    print("Please enter two different cards.")
                    continue
                break
            except ValueError as e:
                print(e)
    else:
        # Random card selection
        temp_deck = deck.copy()
        random.shuffle(temp_deck)
        my_cards = [temp_deck[0], temp_deck[1]]
        
        # Remove player's cards from the actual deck
        for card in my_cards:
            if card in deck:
                deck.remove(card)
        
    print("\nYour cards:")
    print(format_cards(my_cards, suits))
    
    # Get flop cards (manual input or random)
    while True:
        flop_choice = input("\nDo you want to enter the flop manually? (y/n): ").lower()
        if flop_choice in ['y', 'n']:
            break
        print("Please answer with 'y' or 'n'.")
    
    if flop_choice == 'y':
        flop = get_user_flop(deck)
    else:
        # Random flop generation
        temp_deck = deck.copy()
        random.shuffle(temp_deck)
        flop = [temp_deck[0], temp_deck[1], temp_deck[2]]
        for card in flop:
            if card in deck:
                deck.remove(card)
    
    print("\nFlop:")
    print(format_cards(flop, suits))
    
    # Analyze all possible hands - specify we're on the flop
    print("\nAnalyzing all possible combinations...")
    ranked_hands = analyze_all_possible_hands(deck, flop, my_cards, suits, street='flop')
    
    # Find your hand's position and stats
    filtered_hands = [
        hand for hand in ranked_hands 
        if set(my_cards) == set(hand['hole_cards'])
    ]
    
    display_hand_rankings(ranked_hands, suits, mode=display_mode)
    
    # Display updated statistics
    print("\nYour Hand Statistics After Flop:")
    if filtered_hands:
        best_hand = filtered_hands[0]
        position_stats = get_detailed_position_stats(ranked_hands, best_hand['position'])

        print(f"Hole Cards: {format_cards(best_hand['hole_cards'], suits)}")
        print(f"Board: {format_cards(flop, suits)}")
        print(f"Your Hand: {format_cards(best_hand['best_hand'], suits)} - {format_best_hand(best_hand['rank'], suits)} ")
        print(f"Cards Used: {best_hand['cards_used']}")
        print(f"Your Tie: {best_hand['position']} - Hands in your tie: {position_stats['hands_in_my_tie']}")
        print(f"Ties above yours: {position_stats['ties_above']} - Total hands above: {position_stats['hands_above']}")
        print(f"Ties below yours: {position_stats['ties_below']} - Total hands below: {position_stats['hands_below']}")
        print(f"Strength: {best_hand['strength']:.2f}%")
        
        # Visualize updated position distribution
        last_position, position_counts = get_position_stats(ranked_hands)
        visualize_my_position(position_counts, best_hand['position'])
    else:
        print("No valid combination found with your cards.")
    
    
    # Analyze turn
    turn_card, deck = analyze_turn(my_cards, flop, deck, suits, display_mode)
    
    # Analyze river
    river_card, deck = analyze_river(my_cards, flop, turn_card, deck, suits, display_mode)
    
    return my_cards, flop, turn_card, river_card, deck, suits

if __name__ == '__main__':
    my_cards, flop, turn_card, river_card, deck, suits = main()
