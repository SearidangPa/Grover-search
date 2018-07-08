from pyquil.quil import Program
from pyquil.api import QVMConnection
from pyquil.gates import *
import numpy as np
import sys
import math 
qvm = QVMConnection()

from pyquil.api import get_devices, QVMConnection

acorn = get_devices(as_dict=True)['19Q-Acorn']
qvm = QVMConnection(acorn)

#return a matrix that help us build the unitary 2(|0><0|)^n - I^n
def make_gate(n):	
	M = np.zeros((2**n, 2**n))            #create 2(|0><0|)^n
	M[0,0] = 2
	Ixn = np.eye(2**n) 	                  #create I^n
	return  (M - Ixn)

#return a matrix that help us build the unitary Uf
def make_UF_gate(n,s):
	I = np.eye(2**n)
	I[s,s] = -1
	return I

#applying the first series of H gates to the first n qubits 
def apply_Hn (n,p):
	for x in range(n):                    
   		p.inst(H(x+4))                    #qubit 3 is broken

def main (n,s):
	p = Program()

	#make all the gates 
	g = make_gate (n)
	Uf = make_UF_gate(n,s)
	p.defgate("RACL",g)
	p.defgate("UF", Uf)
 
	apply_Hn(n, p)                              #applying the first series of H gates to the first n qubits
	p.inst(X(n+4), H(n+4))                       #get the |-> qubit into our system
	
	r = int ((math.pi * (2 ** (n/2))/4))      #r is the number of iteration 
	for i in range (r):
		p.inst(("UF", *range(4,n+4)))              #apply Uf 
		apply_Hn(n, p)                            #applying the second series of H gates to the first n qubits

		p.inst(("RACL", *range (4,n+4)))          #applying the unitary 2(|0><0|)^n - I^n
		apply_Hn(n, p)                           #applying the third series of H gates to the first n qubits
	   		
	#Make the Measurement 
	classical_regs = [*range(n)] 
	for i in range (n):
		p.measure(i+4,i)
	result = qvm.run(p, classical_regs)

	#convert the result from binary to decimal 
	t = 0
	for i in range (n):
		t += (2**i)*result[0][n-1-i]
	
	return t


if __name__ == '__main__':
	#code used to collect data for the success of different sized algorithms under realistic noise
	for i in range (1,6):                   #testing for program of size from 1 to 5 qubits 
		count = 0 
		for j in range (100):                  #repeat 100 times for each size
			if main(i,1) == 1: 
				count += 1
		print ("the success rate for n = ", i, " is ",count)


