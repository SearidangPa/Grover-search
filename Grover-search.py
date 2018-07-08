from pyquil.quil import Program
from pyquil.api import QVMConnection
from pyquil.gates import *
import numpy as np
import sys
import math 
qvm = QVMConnection()

#return a matrix that help us create unitary 2(|0><0|)^n - I^n
def make_gate(n):	
	M = np.zeros((2**n, 2**n))            #create 2(|0><0|)^n
	M[0,0] = 2
	Ixn = np.eye(2**n) 	                  #create I^n
	return  (M - Ixn)

#return a matrix that help us create unitary Uf
def make_UF_gate(n,s):
	I = np.eye(2**n)
	I[s,s] = -1
	return I

#applying the first series of H gates to the first n qubits 
def apply_Hn (p):
	for x in range(n):                    
   		p.inst(H(x))
   		
#our main program
def main (n,s):
	p = Program()

	#make all the gates 
	g = make_gate (n)
	Uf = make_UF_gate(n,s)
	p.defgate("RACL",g)
	p.defgate("UF", Uf)
 
	apply_Hn(p)                              #applying the first series of H gates to the first n qubits
	p.inst(X(n), H(n))                       #get the |-> qubit into our system
	
	r = int ((math.pi * (2 ** (n/2))/4))      #r is the number of iteration 
	for i in range (r):
		p.inst(("UF", *range(n)))              #apply Uf 
		apply_Hn(p)                            #applying the second series of H gates to the first n qubits

		p.inst(("RACL", *range (n)))          #applying the unitary 2(|0><0|)^n - I^n
		apply_Hn(p)                           #applying the third series of H gates to the first n qubits
	   		
	#Make the Measurement 
	classical_regs = [*range(n)] 
	for i in range (n):
		p.measure(i,i)
	result = qvm.run(p, classical_regs)
	#print (result)

	#convert the result from binary to decimal 
	t = 0
	for i in range (n):
		t += (2**i)*result[0][n-1-i]
	print ("the answer is ", t)
	



if __name__ == '__main__':
	n = int (sys.argv[1])
	s = int (sys.argv[2])
	main(n,s)



