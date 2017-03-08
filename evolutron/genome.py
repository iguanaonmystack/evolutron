import random
import struct

class Genome(object):
    def __init__(self, inputs, outputs):
        self.size = 0
        self.hue = 0
        self.predator = 0
        self.hidden_neurons = 0
        self.hidden0_weights = []
        self.output_weights = []

        # These are not part of the genome but used to speed up calculations
        self._inputs = inputs
        self._outputs = outputs


    @classmethod
    def from_random(cls, inputs, outputs):
        self = cls(inputs, outputs)
        self.size = random.randint(7, 20)
        self.hue = random.random() * 100
        self.predator = random.random() * 2 - 1
        self.hidden_neurons = random.randint(3, 7)

        # For each hidden neuron, generate the weight for each input and for
        # each output
        for i in range(self.hidden_neurons):
            for j in range(inputs):
                self.hidden0_weights.append(random.random() * 2 - 1)
            for j in range(outputs):
                self.output_weights.append(random.random() * 2 - 1)
        assert len(self.hidden0_weights) == self.hidden_neurons * self._inputs
        assert len(self.output_weights) == self.hidden_neurons * self._outputs
        return self


    def mutate(self, rate=0.01):
        new = self.__class__(self._inputs, self._outputs)
        new.size = int(round(self._mutate_single(self.size, rate, min=7)))
        new.hue = self._mutate_single(self.hue, rate) % 100.0
        new.predator = self._mutate_single(self.predator, rate)
        new.hidden_neurons = int(round(self._mutate_single(self.hidden_neurons, rate, min=3)))
        iterate_over = self.hidden_neurons
        if new.hidden_neurons < self.hidden_neurons:
            iterate_over = new.hidden_neurons
        i = 0
        for i in range(iterate_over):
            offset = self._inputs * i
            for j in range(self._inputs):
                new.hidden0_weights.append(
                    self._mutate_single(self.hidden0_weights[offset + j], rate))
            offset = self._outputs * i
            for j in range(self._outputs):
                new.output_weights.append(
                    self._mutate_single(self.output_weights[offset + j], rate))
        while i < new.hidden_neurons - 1:
            # the genome mutated to desire more hidden neurons
            # so add random numbers to increase the weight part of the genome
            for j in range(self._inputs):
                new.hidden0_weights.append(random.random() * 2 - 1) 
            for j in range(self._outputs):
                new.output_weights.append(random.random() * 2 - 1) 
            i += 1
        assert len(new.hidden0_weights) == new.hidden_neurons * new._inputs, \
            '%s %s %s'%(len(new.hidden0_weights), new.hidden_neurons, new._inputs)
        assert len(new.output_weights) == new.hidden_neurons * new._outputs, \
            '%s %s %s'%(len(new.output_weights), new.hidden_neurons, new._outputs)
        return new


    def _mutate_single(self, value, rate, min=None):
        r = random.random()
        if r < rate:
            value += random.random() * 2 - 1
        if min is not None and value < min:
            value = min
        return value


    @classmethod
    def from_parents(cls, p1, p2, rate=0.01):
        new = cls(p1._inputs, p1._outputs) # currently does not vary
        new.size = p1.size if random.random() < 0.5 else p2.size
        new.hue = p1.hue + p2.hue / 2
        new.predator = p1.predator if random.random() < 0.5 else p2.predator
        new.hidden_neurons = (
            p1.hidden_neurons if random.random() < 0.5 else p2.hidden_neurons)

        # assign p1 to be the parent with fewer hidden neurons:
        if p1.hidden_neurons > p2.hidden_neurons:
            p1, p2 = p2, p1

        assert p1._inputs == 8
        assert p2._inputs == 8
        assert new._inputs == 8
        for i in range(new.hidden_neurons):
            offset = new._inputs * i
            for j in range(new._inputs):
                if offset >= p1.hidden_neurons:
                    parent = p2
                else:
                    parent = p1 if random.random() < 0.5 else p2
                new.hidden0_weights.append(parent.hidden0_weights[offset + j])
            offset = new._outputs * i
            for j in range(new._outputs):
                if offset >= p1.hidden_neurons:
                    parent = p2
                else:
                    parent = p1 if random.random() < 0.5 else p2
                new.output_weights.append(parent.output_weights[offset + j])
        new = new.mutate(rate)
        return new


    def __str__(self):
        return 'Genome:\n  ' + '\n  '.join([str(s) for s in (
            self.size,
            self.hue,
            self.predator,
            self.hidden_neurons,
            self.hidden0_weights,
            self.output_weights,
        )])

    
    def dump(self):
        return {
            'size': self.size,
            'hue': self.hue,
            'predator': self.predator,
            'hidden_neurons': self.hidden_neurons,
            'hidden0_weights': self.hidden0_weights,
            'output_weights': self.output_weights,
        }


if __name__ == '__main__':
    random.seed(1)
    g = Genome.from_random(1, 1)
    print(g)
    for i in range(10000):
        g = g.mutate(0.01)
        print(g)
