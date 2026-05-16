# runtime/attention/attention_history.py

import copy
from collections import deque


class AttentionHistory:

    def __init__(self, maxlen=20):

        self.history = deque(maxlen=maxlen)

    def add_snapshot(self, attention_map):

        self.history.append(copy.deepcopy(attention_map.all_weights()))

    def get_history(self):

        return list(self.history)
