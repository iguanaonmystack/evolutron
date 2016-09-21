import random
import struct

class Genome(object):
    def __init__(self, data):
        self.data = data

    @classmethod
    def from_random(cls, inputs, outputs):
        radius = random.randint(5, 20)
        num_hidden_neurons = random.randint(1, 8)
        gene = [
            radius,
            num_hidden_neurons
        ]
        num_weights = inputs + outputs
        for i in range(num_hidden_neurons * num_weights):
            gene.append(random.random() * 2 - 1)
        return cls(gene)

    def mutate(self, rate=0.01):
        newdata = self.data[:]
        for i, part in enumerate(newdata):
            r = random.random() * 2 - 1
            if r < rate:
                part += r * (part / 8)
            newdata[i] = part
        return self.__class__(newdata)

    def __repr__(self):
        return "Genome('''%s''')" % (self.data,)

    def __str__(self):
        s = []
        for item in self.data:
            s.append("%s" % item)
        return ' '.join(s)


