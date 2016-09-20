import random
import struct

class Genome(object):
    def __init__(self, data):
        self.data = data

    @classmethod
    def from_random(cls):
        import characters
        # gene format:
        '''
            radius (8 bits, values above 25 ignored)
            num_hidden_neurons (8 bits, values above 8 ignored)
            neuron_weights flatened (struct.pack int), normalised to -1/1
        '''
        num_hidden_neurons = random.randint(1, 8)
        gene = [
            random.randint(0, 16),
            num_hidden_neurons,
        ]
        num_weights = characters.Character.brain_inputs + characters.Character.brain_outputs
        for i in range(num_hidden_neurons * num_weights):
            gene.append(random.random())
        return cls(gene)

    def mutate(self, rate=0.01):
        newdata = self.data[:]
        for i, part in enumerate(newdata):
            r = random.random()
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


