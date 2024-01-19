import random

# This is main function that is connected to the Test button. You don't need to touch it.
def prime_test(N, k):
	return fermat(N,k), miller_rabin(N,k)

def mod_exp(x, y, N): 
	if y == 0:
		return 1
	z = mod_exp(x,y//2,N)
	if y%2 == 0:
		return (z**2) % N
	else:
		return (x*(z**2))% N
	
  
def fprobability(k):
    return 1 - (0.5 ** k)

# You will need to implement this function and change the return value.   
def mprobability(k):
    return 0.0


def fermat(N,k):
	low = 2
	hi = N-1
	for i in range(k):
		a = random.randint(low,hi)
		mod_result = mod_exp(a,N-1,N)
		if mod_result != 1:
			return 'composite'
	return 'prime'


def miller_rabin(N,k):
	low = 2
	hi = N-1
	for i in range(k):
		a = random.randint(low,hi)
		exponent = N-1
		while True:
			mod_result = mod_exp(a,exponent,N)
			if mod_result != 1 and mod_result != N-1:
				return 'composite'
			if (exponent)%2 == 0:
				exponent = int(exponent*0.5)
			else: 
				break
			if mod_result == N-1:
				break
	print("returning prime")
	return 'prime'
