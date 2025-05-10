'''
LAB 3

simple regex engine

made by Kostiuk Ostap
'''

class State:
    '''
    represents a state in the NFA
    '''
    def __init__(self, state_id):
        self.id = state_id
        self.transitions = {}
        self.is_final = False

    def add_transition(self, symbol, state):
        """
        adds a transition from the state to another state on a given symbol4
        """
        if symbol not in self.transitions:
            self.transitions[symbol] = set()
        self.transitions[symbol].add(state)

class RegexFSM:
    '''
    Finite State Machine for regular expressions
    '''
    def __init__(self, regex):
        self.regex = regex

        self.tokens = self.parse_regex(regex)

        self.positions = {i+1: (symbol, operator) for i, (symbol, operator) in enumerate(self.tokens)}
        
        # initializing the NFA components
        self.states = {}
        self.start_state = None
        self.nullable = {}
        self.initial = set()
        self.final = set()
        self.follow = {}

        self.build_nfa()

    def parse_regex(self, regex):
        """
        Breaks down the regex into tokens (symbol, operator)
        """
        tokens = []
        i = 0
        while i < len(regex):

            if i + 1 < len(regex) and regex[i+1] in '*+':
                tokens.append((regex[i], regex[i+1]))
                i += 2

            else:
                tokens.append((regex[i], ''))
                i += 1

        return tokens

    def build_nfa(self):
        """
        main function to build the NFA
        """

        for pos in self.positions:
            self.states[pos] = State(pos)

        self.start_state = State(0)
        self.states[0] = self.start_state

        self.nullable = self.check_nullable()
        self.initial = self.compute_initial()
        self.follow = self.compute_follow()
        self.final = self.compute_final()

        for pos in self.initial:
            symbol, _ = self.positions[pos]
            self.start_state.add_transition(symbol, self.states[pos])

            if symbol == '.':
                self.start_state.add_transition(None, self.states[pos])
        

        for src in self.follow:
            src_state = self.states[src]
            for dst in self.follow[src]:
                symbol, _ = self.positions[dst]
                src_state.add_transition(symbol, self.states[dst])

                if symbol == '.':
                    src_state.add_transition(None, self.states[dst])

        for pos in self.final:
            self.states[pos].is_final = True

    def check_nullable(self):
        """
        checking if the position can be empty (for * and +)
        """
        nullable = {}
        for pos, (_, op) in self.positions.items():
            nullable[pos] = op == '*'
        return nullable

    def compute_initial(self):
        """
        compute the first positions for each position
        """
        first = set()
        i = 0

        while i < len(self.tokens):
            pos = i + 1
            first.add(pos)

            if self.nullable[pos]:
                i += 1
            else:
                break

        return first

    def compute_follow(self):
        """
        compute the follow positions for each position
        """
        follow = {pos: set() for pos in self.positions}
        for i, (_, op) in enumerate(self.tokens):
            current_pos = i + 1

            if op in ('*', '+'):
                follow[current_pos].add(current_pos)  # cycle

            if i < len(self.tokens) - 1:
                next_pos = i + 2
                follow[current_pos].add(next_pos)

                j = i + 1
                while j < len(self.tokens) - 1 and self.nullable[next_pos]:
                    j += 1
                    next_pos = j + 1
                    follow[current_pos].add(next_pos)

        return follow

    def compute_final(self):
        """
        compute the final positions for each position
        """
        last = set()
        i = len(self.tokens) - 1
        while i >= 0:
            pos = i + 1
            last.add(pos)

            if self.nullable[pos]:
                i -= 1
            else:
                break

        return last

    def check_string(self, s):
        """
        checks if the string is accepted by the FSM
        """
        current_states = {self.start_state}
        

        for char in s:
            next_states = set()
            
            for state in current_states:

                possible_symbols = []
                if char in state.transitions:
                    possible_symbols.append(char)
                if '.' in state.transitions:
                    possible_symbols.append('.')
                if None in state.transitions:
                    possible_symbols.append(None)
                

                for symbol in possible_symbols:

                    if symbol == '.' or symbol is None:
                        next_states.update(state.transitions.get('.', set()))
                        next_states.update(state.transitions.get(None, set()))
                    else:
                        next_states.update(state.transitions.get(symbol, set()))
            
            current_states = next_states
            if not current_states:
                return False

        return any(state.is_final for state in current_states)

if __name__ == "__main__":
    regex_pattern = "a*4.+hi"
    regex_compiled = RegexFSM(regex_pattern)
    
    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))        # True
    print(regex_compiled.check_string("meow"))        # False
