# runtime/attention/attention_decay.py


class AttentionDecay:

    def __init__(self, decay_rate=0.95):

        self.decay_rate = decay_rate

    def tick(self, field):

        for node_id in list(field.node_attention.keys()):

            field.node_attention[node_id] *= self.decay_rate
