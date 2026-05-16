# runtime/attention/emergent_focus.py


class EmergentFocus:

    def detect(self, field, threshold=3.0):

        focus = []

        for node_id, value in field.node_attention.items():

            if value >= threshold:

                focus.append((node_id, value))

        return sorted(
            focus,
            key=lambda x: x[1],
            reverse=True,
        )
