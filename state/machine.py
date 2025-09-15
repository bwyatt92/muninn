from enum import Enum
import threading
import time
from typing import Callable, Optional, Dict, Any

class MuninnState(Enum):
    SLEEPING = "sleeping"
    LISTENING = "listening"
    RECORDING = "recording"
    PLAYING = "playing"
    PROCESSING = "processing"

class StateMachine:
    def __init__(self):
        self.state = MuninnState.SLEEPING
        self.state_lock = threading.Lock()
        self.state_callbacks: Dict[MuninnState, list] = {state: [] for state in MuninnState}
        self.transition_callbacks: Dict[tuple, list] = {}
        self.running = False

    def register_state_callback(self, state: MuninnState, callback: Callable):
        if state not in self.state_callbacks:
            self.state_callbacks[state] = []
        self.state_callbacks[state].append(callback)

    def register_transition_callback(self, from_state: MuninnState, to_state: MuninnState, callback: Callable):
        transition = (from_state, to_state)
        if transition not in self.transition_callbacks:
            self.transition_callbacks[transition] = []
        self.transition_callbacks[transition].append(callback)

    def get_state(self) -> MuninnState:
        with self.state_lock:
            return self.state

    def transition_to(self, new_state: MuninnState, context: Optional[Dict[str, Any]] = None):
        with self.state_lock:
            old_state = self.state
            if old_state == new_state:
                return

            print(f"State transition: {old_state.value} -> {new_state.value}")

            # Call transition callbacks
            transition = (old_state, new_state)
            if transition in self.transition_callbacks:
                for callback in self.transition_callbacks[transition]:
                    try:
                        callback(old_state, new_state, context or {})
                    except Exception as e:
                        print(f"Error in transition callback: {e}")

            self.state = new_state

            # Call state entry callbacks
            if new_state in self.state_callbacks:
                for callback in self.state_callbacks[new_state]:
                    try:
                        callback(context or {})
                    except Exception as e:
                        print(f"Error in state callback: {e}")

    def is_state(self, state: MuninnState) -> bool:
        return self.get_state() == state

    def start(self):
        self.running = True
        self.transition_to(MuninnState.SLEEPING)

    def stop(self):
        self.running = False