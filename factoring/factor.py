import dwavebinarycsp as dbc
from dwave.embedding import embed_bqm, unembed_sampleset
from dwave.system.samplers import DWaveSampler
import minorminer
from collections import OrderedDict
from helpers.convert import to_base_ten

# Function for converting the response to a dict of integer values
def response_to_dict(response):
    results_dict = OrderedDict()
    for sample, energy in response.data(['sample', 'energy']):
        # Convert A and B from binary to decimal
        a, b = to_base_ten(sample)
        # Aggregate results by unique A and B values (ignoring internal circuit variables)
        if (a, b) not in results_dict:
            results_dict[(a, b)] = energy
            
    return results_dict

# Set an integer to factor
P = 45

# A binary representation of P ("{:06b}" formats for 6-bit binary)
bP = "{:06b}".format(P)
print(bP)

csp = dbc.factories.multiplication_circuit(3)

# Convert the CSP into BQM bqm
bqm = dbc.stitch(csp, min_classical_gap=.1)
# Print a sample coefficient (one of the programable inputs to a D-Wave system)
print(bqm.linear)

# Our multiplication_circuit() creates these variables
p_vars = ['p0', 'p1', 'p2', 'p3', 'p4', 'p5']

# Convert P from decimal to binary
fixed_variables = dict(zip(reversed(p_vars), "{:06b}".format(P)))
fixed_variables = {var: int(x) for(var, x) in fixed_variables.items()}

# Fix product variables
for var, value in fixed_variables.items():
    bqm.fix_variable(var, value)
    
# Confirm that a P variable has been removed from the BQM, for example, "p0"
print("Variable p0 in BQM: ", 'p0' in bqm)
print("Variable a0 in BQM: ", 'a0' in bqm)


# Use a D-Wave system as the sampler
# sampler = DWaveSampler(solver={'qpu': True})  # Some accounts need to replace this line with the next:
sampler = DWaveSampler(solver='DW_2000Q_2_1', token='DEV-289c9dcb0d1d85f3a9059f77fd53bc84e3935d52')
_, target_edgelist, target_adjacency = sampler.structure



# Find an embedding
embedding = minorminer.find_embedding(bqm.quadratic, target_edgelist)
if bqm and not embedding:
    raise ValueError("no embedding found")

bqm_embedded = embed_bqm(bqm, embedding, target_adjacency, 3.0)


# Confirm mapping of variables from a0, b0, etc to indexed qubits 
print("Variable a0 in embedded BQM: ", 'a0' in bqm_embedded)
print("First five nodes in QPU graph: ", sampler.structure.nodelist[:5])

kwargs = {}
if 'num_reads' in sampler.parameters:
    kwargs['num_reads'] = 5
if 'answer_mode' in sampler.parameters:
    kwargs['answer_mode'] = 'histogram'

# Request num_reads samples
kwargs['num_reads'] = 1000
response = sampler.sample(bqm_embedded, **kwargs)

# Convert back to the problem graph
response = unembed_sampleset(response, embedding, source_bqm=bqm)

results = response_to_dict(response)
print(results)