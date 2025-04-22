import random
from collections import Counter, defaultdict
from colorama import Fore, Style, init
import matplotlib.pyplot as plt
from officialcode import *

# Initialize colorama for colored terminal output
init(autoreset=True)

class PokerPlayer:
    """
    Represents a player in a Texas Hold'em poker game.
    
    Attributes:
        name (str): Player name
        hole_cards (list): Player's private cards
        chips (int): Player's chip count
        current_bet (int): Player's current bet in the round
        position (str): Player's position in the game
        position_order (int): Numerical order for determining betting sequence
        folded (bool): Whether the player has folded this hand
    """
    def __init__(self, name, chips=1000, position=None):
        self.name = name
        self.hole_cards = []
        self.chips = chips
        self.current_bet = 0
        self.position = position
        self.position_order = 0
        self.folded = False
    
    def receive_cards(self, cards):
        """Give hole cards to the player."""
        self.hole_cards = cards
    
    def place_bet(self, amount):
        """Place a bet of the specified amount."""
        if amount > self.chips:
            amount = self.chips  # All-in
        
        self.chips -= amount
        self.current_bet += amount
        return amount
    
    def fold(self):
        """Fold the current hand."""
        self.folded = True
    
    def reset_for_new_hand(self):
        """Reset player state for a new hand."""
        self.hole_cards = []
        self.current_bet = 0
        self.folded = False


class PokerGame:
    """
    Manages a Texas Hold'em poker game.
    
    Attributes:
        num_players (int): Number of players in the game
        players (list): List of PokerPlayer objects
        show_all_cards (bool): Whether to show all players' cards
        deck (list): Current deck of cards
        suits (dict): Dictionary of suits with color codes
        community_cards (list): Shared community cards
        pot (int): Total chips in the pot
        current_bet (int): Current bet that players need to match
        small_blind (int): Small blind amount
        big_blind (int): Big blind amount
    """
    def __init__(self):
        """Initialize the poker game with default values."""
        self.num_players = 0
        self.players = []
        self.show_all_cards = True  # Always show all cards since a single person is playing for everyone
        self.deck, self.suits = create_deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.small_blind = 5
        self.big_blind = 10
    
    def setup_game(self):
        """Set up the poker game by gathering user preferences."""
        self._get_player_count()
        self._setup_player_positions()
        
        # Sort players by position order for betting sequence
        self.players.sort(key=lambda player: player.position_order)
    
    def _get_player_count(self):
        """Prompt user for the number of players."""
        while True:
            try:
                self.num_players = int(input("\nEnter the number of players (2-9): "))
                if 2 <= self.num_players <= 9:
                    break
                else:
                    print("Please enter a number between 2 and 9.")
            except ValueError:
                print("Please enter a valid number.")
    
    def _setup_player_positions(self):
        """Set up player positions for all players."""
        # In 2-player poker, one player is both BTN and SB, the other is BB
        if self.num_players == 2:
            position_names = ["BTN/SB", "BB"]
            for i in range(self.num_players):
                player = PokerPlayer(
                    name=f"P{i+1}",
                    position=position_names[i]
                )
                player.position_order = i + 1
                self.players.append(player)
        else:
            # For 3+ players, use standard positions
            positions = []
            # Always have BTN, SB, BB
            positions.extend(["BTN", "SB", "BB"])

            # Add remaining positions based on table size
            if self.num_players >= 4:
                positions.append("UTG")
            if self.num_players >= 5:
                positions.append("UTG+1")
            if self.num_players >= 6:
                positions.append("MP")
            if self.num_players >= 7:
                positions.append("MP+1")
            if self.num_players >= 8:
                positions.append("HJ")
            if self.num_players >= 9:
                positions.append("CO")

            # Arrange positions in playing order
            # Correct order is SB, BB, UTG, UTG+1, MP, MP+1, HJ, CO, BTN
            playing_order = positions[1:] + [positions[0]]  # Move BTN to the end

            for i in range(self.num_players):
                position = positions[i]
                position_order = playing_order.index(position) + 1

                player = PokerPlayer(
                    name=f"P{i+1}",
                    position=position
                )
                player.position_order = position_order
                self.players.append(player)
    
    def deal_hole_cards(self):
        """Deal two hole cards to each player."""
        for player in self.players:
            cards = pick_random_cards(self.deck, 2)
            player.receive_cards(cards)
    
    def deal_community_cards(self, stage):
        """
        Deal community cards based on the stage.
        
        Args:
            stage (str): 'flop', 'turn', or 'river'
        """
        if stage == 'flop':
            cards = pick_random_cards(self.deck, 3)
            self.community_cards.extend(cards)
            print(f"\n--- FLOP ---")
        elif stage == 'turn':
            card = pick_random_cards(self.deck, 1)
            self.community_cards.extend(card)
            print(f"\n--- TURN ---")
        elif stage == 'river':
            card = pick_random_cards(self.deck, 1)
            self.community_cards.extend(card)
            print(f"\n--- RIVER ---")
        
        print(format_cards(self.community_cards, self.suits))

    def betting_round(self, starting_player_idx=0, is_preflop=False):
        """
        Conduct a betting round.

        Args:
            starting_player_idx (int): Index of the player who starts the betting
            is_preflop (bool): Whether this is the pre-flop betting round

        Returns:
            bool: True if multiple players are still active, False otherwise
        """
        if not is_preflop:
            self.current_bet = 0

        # Calculate current pot (including all current bets)
        current_pot = self.pot + sum(player.current_bet for player in self.players)

        # Track which players have acted in this round
        players_acted = set()

        # Count active (non-folded) players
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) <= 1:
            return False

        # Reset current bet for all players for this round if not preflop
        if not is_preflop:
            for player in self.players:
                player.current_bet = 0

        current_idx = starting_player_idx
        round_complete = False

        print("\n--- BETTING ROUND ---")

        while not round_complete:
            current_player = self.players[current_idx]

            # Skip folded players
            if current_player.folded:
                current_idx = (current_idx + 1) % len(self.players)
                continue
            
            # Recalculate current pot for display
            current_pot = self.pot + sum(player.current_bet for player in self.players)

            # Handle player's action
            self._handle_player_action(current_player, current_pot)

            # Mark this player as having acted
            players_acted.add(current_player)

            # Check if the round is complete:
            # 1. All active players have acted
            # 2. All active players have either folded or matched the current bet
            active_players = [p for p in self.players if not p.folded]
            if len(active_players) <= 1:
                return False  # Only one player left

            if all(p in players_acted for p in active_players) and all(
                p.folded or p.current_bet == self.current_bet for p in active_players
            ):
                round_complete = True

            # Move to the next player
            current_idx = (current_idx + 1) % len(self.players)

        # Add all bets to the pot
        for player in self.players:
            self.pot += player.current_bet
            player.current_bet = 0

        return True

    def _handle_player_action(self, player, current_pot):
        """
        Handle betting actions for a player.
        
        Args:
            player (PokerPlayer): The player making a decision
            current_pot (int): The current pot size including all bets
        """
        # Display cards and betting information
        print(f"\n{player.name}'s turn ({player.position}):")
        print(f"Hole cards: {format_cards(player.hole_cards, self.suits)}")
        print(f"Chips: {player.chips}")
        print(f"Current bet: {self.current_bet}")
        print(f"Pot: {current_pot}")
        
        # Determine available actions and their minimum amounts
        actions = []
        
        # Fold should always be an option
        actions.append("fold")
        
        if self.current_bet == 0:
            min_bet = self.big_blind
            actions.extend(["check", f"bet (min {min_bet})"])
        else:
            call_amount = self.current_bet - player.current_bet
            if call_amount >= player.chips:
                # Player can only call all-in
                actions.append(f"call {call_amount}")
            else:
                min_raise = 2 * self.current_bet - player.current_bet
                actions.extend([f"call {call_amount}", f"raise (min {min_raise})"])
        
        # Get action from user
        valid_action = False
        while not valid_action:
            action_str = ", ".join(actions)
            action_input = input(f"{player.name} ({action_str}): ").lower()
            
            # Parse the action
            if action_input == "check" and "check" in action_str:
                action = "check"
                valid_action = True
            
            elif action_input == "fold":
                action = "fold"
                valid_action = True
            
            elif action_input.startswith("call") and any(a.startswith("call") for a in actions):
                action = "call"
                call_amount = self.current_bet - player.current_bet
                valid_action = True
            
            elif action_input.startswith("bet") and any(a.startswith("bet") for a in actions):
                action = "bet"
                parts = action_input.split()
                if len(parts) > 1 and parts[1].isdigit():
                    bet_amount = int(parts[1])
                    min_bet = self.big_blind
                    if bet_amount < min_bet:
                        print(f"Bet must be at least {min_bet}.")
                    elif bet_amount > player.chips:
                        print(f"Player doesn't have enough chips. Maximum: {player.chips}")
                    else:
                        valid_action = True
                        self.current_bet = bet_amount
                else:
                    # Ask for the bet amount
                    min_bet = self.big_blind
                    while True:
                        try:
                            bet_amount = int(input(f"Enter bet amount (minimum {min_bet}): "))
                            if bet_amount < min_bet:
                                print(f"Bet must be at least {min_bet}.")
                            elif bet_amount > player.chips:
                                print(f"Player doesn't have enough chips. Maximum: {player.chips}")
                            else:
                                valid_action = True
                                self.current_bet = bet_amount
                                break
                        except ValueError:
                            print("Please enter a valid number.")
            
            elif action_input.startswith("raise") and any(a.startswith("raise") for a in actions):
                action = "raise"
                parts = action_input.split()
                if len(parts) > 1 and parts[1].isdigit():
                    raise_amount = int(parts[1])
                    min_raise = 2 * self.current_bet - player.current_bet
                    if raise_amount < min_raise:
                        print(f"Raise must be at least {min_raise}.")
                    elif raise_amount > player.chips:
                        print(f"Player doesn't have enough chips. Maximum: {player.chips}")
                    else:
                        valid_action = True
                        self.current_bet = raise_amount
                else:
                    # Ask for the raise amount
                    min_raise = 2 * self.current_bet - player.current_bet
                    while True:
                        try:
                            raise_amount = int(input(f"Enter raise amount (minimum {min_raise}): "))
                            if raise_amount < min_raise:
                                print(f"Raise must be at least {min_raise}.")
                            elif raise_amount > player.chips:
                                print(f"Player doesn't have enough chips. Maximum: {player.chips}")
                            else:
                                valid_action = True
                                self.current_bet = raise_amount
                                break
                        except ValueError:
                            print("Please enter a valid number.")
            
            if not valid_action:
                print(f"Invalid action. Please choose from: {action_str}")
        
        # Handle the chosen action
        if action == "check":
            print(f"{player.name} checks.")
        
        elif action == "call":
            call_amount = self.current_bet - player.current_bet
            if call_amount > player.chips:
                call_amount = player.chips  # All-in
            
            player.place_bet(call_amount)
            print(f"{player.name} calls {call_amount}.")
        
        elif action == "bet":
            player.place_bet(self.current_bet)
            print(f"{player.name} bets {self.current_bet}.")
        
        elif action == "raise":
            # Find out how much more the player needs to bet
            additional_amount = self.current_bet - player.current_bet
            player.place_bet(additional_amount)
            print(f"{player.name} raises to {self.current_bet}.")
        
        elif action == "fold":
            player.fold()
            print(f"{player.name} folds.")



    def post_blinds(self):
        """Post small and big blinds."""
        if self.num_players == 2:
            # In 2-player poker, BTN/SB posts small blind
            btn_sb_player = next(p for p in self.players if p.position == "BTN/SB")
            bb_player = next(p for p in self.players if p.position == "BB")

            # Post small blind
            sb_amount = btn_sb_player.place_bet(self.small_blind)
            print(f"\n{btn_sb_player.name} posts SB of {sb_amount}")

            # Post big blind
            bb_amount = bb_player.place_bet(self.big_blind)
            print(f"{bb_player.name} posts big blind of {bb_amount}")
        else:
            # Standard blinds for 3+ players
            small_blind_player = next(p for p in self.players if p.position == "SB")
            big_blind_player = next(p for p in self.players if p.position == "BB")

            # Post small blind
            sb_amount = small_blind_player.place_bet(self.small_blind)
            print(f"\n{small_blind_player.name} posts SB of {sb_amount}")

            # Post big blind
            bb_amount = big_blind_player.place_bet(self.big_blind)
            print(f"{big_blind_player.name} posts big blind of {bb_amount}")

        # Set current bet to big blind
        self.current_bet = self.big_blind
    
    def determine_winner(self):
        """
        Determine the winner of the hand.
        
        Returns:
            PokerPlayer: The winning player
        """
        active_players = [p for p in self.players if not p.folded]
        
        # If only one player remains, they win
        if len(active_players) == 1:
            return active_players[0]
        
        # Calculate best hand for each player
        player_best_hands = []
        
        for player in active_players:
            # Generate all possible 5-card hands
            all_cards = player.hole_cards + self.community_cards
            possible_hands = form_hands_from_board(player.hole_cards, self.community_cards)
            
            # Find the best hand
            best_hand = max(possible_hands, key=lambda hand: identify_hand_ranking(hand))
            hand_rank = identify_hand_ranking(best_hand)
            
            player_best_hands.append({
                'player': player,
                'best_hand': best_hand,
                'rank': hand_rank
            })
        
        # Sort by hand rank (best first)
        player_best_hands.sort(key=lambda x: x['rank'], reverse=True)
        
        # Return the player with the best hand
        return player_best_hands[0]['player']
    
    def display_community_cards(self):
        """Display the community cards."""
        if self.community_cards:
            print("\nCommunity cards:")
            print(format_cards(self.community_cards, self.suits))
        else:
            print("\nNo community cards yet.")
    
    def display_player_cards(self):
        """Display all players' hole cards."""
        print("\nPlayers' hole cards:")
        for player in self.players:
            if not player.folded:
                print(f"{player.name} ({player.position}): {format_cards(player.hole_cards, self.suits)}")
    
    def play_hand(self):
        """Play a complete hand of Texas Hold'em."""
        print("\n===== NEW HAND =====")
        
        # Reset the deck and shuffle
        self.deck, self.suits = create_deck()
        random.shuffle(self.deck)
        
        # Reset all players for a new hand
        for player in self.players:
            player.reset_for_new_hand()
        
        # Clear community cards and pot
        self.community_cards = []
        self.pot = 0
        
        # Deal hole cards
        self.deal_hole_cards()
        
        # Show all hole cards
        self.display_player_cards()
        
        # Post blinds
        self.post_blinds()
        
        # Pre-flop betting round
        # Betting starts from the player after the big blind
        bb_idx = next(i for i, p in enumerate(self.players) if p.position == "BB")
        starting_idx = (bb_idx + 1) % len(self.players)
        
        print("\n--- PRE-FLOP ---")
        if not self.betting_round(starting_idx, is_preflop=True):
            return self._end_hand()
        
        # Flop
        self.deal_community_cards('flop')
        # Betting starts from first active player after the button
        button_idx = next(i for i, p in enumerate(self.players) if p.position == "BTN")
        starting_idx = (button_idx + 1) % len(self.players)
        if not self.betting_round(starting_idx):
            return self._end_hand()
        
        # Turn
        self.deal_community_cards('turn')
        if not self.betting_round(starting_idx):
            return self._end_hand()
        
        # River
        self.deal_community_cards('river')
        if not self.betting_round(starting_idx):
            return self._end_hand()
        
        # Showdown
        return self._end_hand(showdown=True)
    
    def _end_hand(self, showdown=False):
        """
        End the current hand and determine the winner.
        
        Args:
            showdown (bool): Whether to show all cards for a showdown
            
        Returns:
            PokerPlayer: The winning player
        """
        # Display all cards if it's a showdown
        if showdown:
            print("\n--- SHOWDOWN ---")
            self.display_player_cards()
        
        # Determine the winner
        winner = self.determine_winner()
        
        # Award the pot
        winner.chips += self.pot
        
        print(f"\n{winner.name} wins {self.pot} chips!")
        
        # Show best hands if it was a showdown
        if showdown:
            active_players = [p for p in self.players if not p.folded]
            for player in active_players:
                possible_hands = form_hands_from_board(player.hole_cards, self.community_cards)
                best_hand = max(possible_hands, key=lambda hand: identify_hand_ranking(hand))
                hand_rank = identify_hand_ranking(best_hand)
                
                print(f"{player.name}'s best hand: {format_best_hand(hand_rank, self.suits)}")
                print(f"  {format_cards(best_hand, self.suits)}")
        
        return winner
    
    def rotate_positions(self):
        """Rotate player positions for the next hand."""
        # Get current positions
        button_player = next(p for p in self.players if p.position == "BTN")
        sb_player = next(p for p in self.players if p.position == "SB")
        bb_player = next(p for p in self.players if p.position == "BB")
        
        # Get indices
        button_idx = self.players.index(button_player)
        sb_idx = self.players.index(sb_player)
        bb_idx = self.players.index(bb_player)
        
        # Clear current positions
        for player in self.players:
            if player.position in ["BTN", "SB", "BB"]:
                player.position = f"Position {player.position_order}"
        
        # Calculate new positions
        new_button_idx = (button_idx + 1) % len(self.players)
        new_sb_idx = (sb_idx + 1) % len(self.players)
        new_bb_idx = (bb_idx + 1) % len(self.players)
        
        # Assign new positions
        self.players[new_button_idx].position = "BTN"
        self.players[new_sb_idx].position = "SB"
        self.players[new_bb_idx].position = "BB"
    
    def display_game_state(self):
        """Display the current game state with chips for all players."""
        print("\n--- CURRENT GAME STATE ---")
        for player in self.players:
            status = " (folded)" if player.folded else ""
            print(f"{player.name} ({player.position}): {player.chips} chips{status}")
    
    def play_game(self, num_hands=5):
        """
        Play multiple hands of Texas Hold'em.
        
        Args:
            num_hands (int): Number of hands to play
        """
        self.setup_game()
        
        for i in range(num_hands):
            print(f"\n\n======= HAND {i+1} of {num_hands} =======")
            
            # Play a hand
            self.play_hand()
            
            # Display game state
            self.display_game_state()
            
            # Check if all but one player is out of chips
            active_players = [p for p in self.players if p.chips > 0]
            if len(active_players) == 1:
                print(f"\n{active_players[0].name} wins the game!")
                break
            
            # Rotate positions for next hand
            if i < num_hands - 1:
                self.rotate_positions()
                
                # Prompt to continue
                input("\nPress Enter to continue to the next hand...")
        
        print("\nGame over! Final chip counts:")
        for player in sorted(self.players, key=lambda p: p.chips, reverse=True):
            print(f"{player.name}: {player.chips} chips")

def main():
    """
    Main function to run the Texas Hold'em poker game.
    """
    # Initialize colorama for colored terminal output
    init(autoreset=True)

    # Create a new poker game
    game = PokerGame()
    
    # Ask how many hands to play
    # num_hands = 0
    # while num_hands <= 0:
    #     try:
    #         num_hands = int(input("\nHow many hands would you like to play? "))
    #         if num_hands <= 0:
    #             print("Please enter a positive number.")
    #     except ValueError:
    #         print("Please enter a valid number.")
    num_hands = 1
    
    # Play the game with the specified number of hands
    game.play_game(num_hands)

if __name__ == "__main__":
    main()
