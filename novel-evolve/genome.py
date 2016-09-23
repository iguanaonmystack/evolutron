import random
import struct

class Genome(object):
    def __init__(self, inputs, outputs):
        self.radius = 0
        self.hidden_neurons = 0
        self.hidden0_weights = []
        self.output_weights = []

        # These are not part of the genome but used to speed up calculations
        self._inputs = inputs
        self._outputs = outputs


    @classmethod
    def from_random(cls, inputs, outputs):
        self = cls(inputs, outputs)
        self.radius = random.randint(5, 20)
        self.hidden_neurons = random.randint(2, 8)
        
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

    def _mutate_single(self, value, rate):
        r = random.random()
        if r < rate:
            value += random.random() * 2 - 1
        return value

    def mutate(self, rate=0.01):
        new = self.__class__(self._inputs, self._outputs)
        new.radius = int(round(self._mutate_single(self.radius, rate)))
        new.hidden_neurons = int(round(self._mutate_single(self.hidden_neurons, rate)))
        iterate_over = self.hidden_neurons
        if new.hidden_neurons < self.hidden_neurons:
            iterate_over = new.hidden_neurons
        for i in range(iterate_over):
            for j in range(self._inputs):
                new.hidden0_weights.append(self._mutate_single(self.hidden0_weights[i], rate))
            for j in range(self._outputs):
                new.output_weights.append(self._mutate_single(self.output_weights[i], rate))
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

    def __str__(self):
        return 'Genome:\n  ' + '\n  '.join([str(s) for s in (
            self.radius,
            self.hidden_neurons,
            self.hidden0_weights,
            self.output_weights,
        )])



if __name__ == '__main__':
    random.seed(1)
    g = Genome.from_random(1, 1)
    print(g)
    for i in range(10000):
        g = g.mutate(0.01)
    print(g)
