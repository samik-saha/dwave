import dwavebinarycsp  
from dwavebinarycsp.factories.csp.circuits import multiplication_circuit  
import neal  
csp = multiplication_circuit(3)  
bqm = dwavebinarycsp.stitch(csp)  
#bqm.fix_variable('a0', 1); bqm.fix_variable('a1', 0); bqm.fix_variable('a2', 1)  
#bqm.fix_variable('b0', 1); bqm.fix_variable('b1', 1); bqm.fix_variable('b2', 0)  
bqm.fix_variable('p0', 1); bqm.fix_variable('p1', 1); bqm.fix_variable('p2', 1);bqm.fix_variable('p3', 1); bqm.fix_variable('p4', 0); bqm.fix_variable('p5', 0)
sampler = neal.SimulatedAnnealingSampler()  
response = sampler.sample(bqm)
for sample in response.samples(n=5):
    print(sample)
#p = next(response.samples(n=1, sorted_by='energy'))  
#print(p['p0'], p['p1'], p['p2'], p['p3'], p['p4'], p['p5'])    # doctest: +SKIP