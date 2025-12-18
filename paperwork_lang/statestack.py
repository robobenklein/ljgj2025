

class StateStack():
    def __init__(self, bottom_state):
        self.current_index = 0
        self.stack_map = {bottom_state.__class__ : 0}
        self.stack = [bottom_state]
        pass

    # Unload the current state
    # Then add and load the new one
    def push_state(self, state):
        self.stack[self.current_index].unload()

        self.current_index += 1
        self.stack_map[state.__class__] = self.current_index
        self.stack.append(state)
        state.load()

    # Unload the current state
    # Then add and load the new one.
    # Returns the new state
    def pop_state(self):
        if self.current_index == 0:
            print(f"No more states to pop, can't pop the only state left")
            return

        self.stack[self.current_index].unload()
        self.current_index -= 1

        self.stack_map.popitem()
        self.stack.pop()

        return self.stack[self.current_index]

    # Transition to an existing state.
    # If its lower in the stack, it will unload the current state, and if it's not temporary (like a pause menu) it will remove the other states up to the new state.
    # If the state is higher, it should not be temporary and will only unload the current state and load the new one
    def transition_to_state(self, state, b_is_temp):
        index = self.stack_map[state.__class__]
        if index == -1 or index == self.current_index:
            print(f"State stack tried to transition to index {index}, if it's not -1 the state is already loaded")
            return self.stack[self.current_index]

        self.stack[self.current_index].unload()
        if index < self.current_index:
            if b_is_temp:
                self.prev_index = self.current_index
            else:
                # Remove the rest
                while self.current_index > index:
                    self.stack_map.popitem()
                    self.stack.pop()
                    self.current_index -= 1

        return self.stack[self.current_index]

    def transition_from_saved_state(self):
        if self.prev_index == -1:
            print(f"State stack has no saved state to transition to")
            return self.stack[self.current_index]

        self.stack[self.current_index].unload()
        self.current_index = self.prev_index
        self.prev_index = -1
        
        return self.stack[self.current_index]
