
from difflib import SequenceMatcher

class LookupInString:
    def __init__(self, x, y, minimum_size=10):
        self.piecewises = piecewise_combinator(x, y, minimum_size)

    def __call__(self, location):
        # TODO make this not incredibly slow
        end_idx = next(idx for idx, (x, _) in enumerate(self.piecewises) if x > location)
        start_idx = end_idx - 1
        proportion = (location - self.piecewises[start_idx][0]) / (self.piecewises[end_idx][0] - self.piecewises[start_idx][0])
        output_location = self.piecewises[start_idx][1] + proportion * (self.piecewises[end_idx][1] - self.piecewises[start_idx][1])
        return output_location


def piecewise_combinator(x, y, minimum_size):
    sm = SequenceMatcher(None, x, y)
    minimum_size = 10
    piecewises = [(0, 0)]
    for block in sm.get_matching_blocks():
        if block.size < minimum_size:
            continue
        piecewises.append((block.a, block.b))
        piecewises.append((block.a + block.size, block.b + block.size))
    piecewises.append((len(x), len(y)))
    return piecewises
