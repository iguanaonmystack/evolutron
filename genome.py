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
        gene = '%s%s' % (
            chr(random.randint(0, 255)), # will be masked to 0b1111
            chr(num_hidden_neurons - 1)) # will be masked to 0b111 and += 1
        for i in range(num_hidden_neurons):
            for k in range(characters.Character.brain_inputs):
                for j in range(4):
                    gene += '%s' % (chr(random.randint(0, 255)))
            for k in range(characters.Character.brain_outputs):
                for j in range(4):
                    gene += '%s' % (chr(random.randint(0, 255)))
        return cls(gene)

    def mutate(self, rate=0.01):
        newdata = []
        for i in range(len(self.data)):
            newbyte = ord(self.data[i])
            for bit in range(8):
                if random.random() < rate:
                    newbyte ^= (1 << bit)
            newdata.append(chr(newbyte))
        return self.__class__(''.join(newdata))

    def __repr__(self):
        return "Genome('''%s''')" % (self.data,)

    def __str__(self):
        s = []
        for c in self.data:
            s.append('{:08b}'.format(ord(c)))
        return ' '.join(s)


