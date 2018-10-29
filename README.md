# Parallelism
Parallelism is a python module intended to simplify the parallelization of existing code.

## Installation
Parallelism can be bundled in a python egg and handled by pip.
```
pip install .
```
or, if you want it installed only user-wide:
```
pip install --user .
```

## Usage
Suppose you have the following function
```
def math_intensive_computation(arg)
	...
	return x
```
Suppose you want to run several instances of this function in parallel on 4 processes, then you can type
```
import parallelism as pll

res = pll.launch_workers([dict(arg=arg1), dict(arg=arg2), ...], 
				         math_intensive_computation, parallelism=4)
```
where _arg1,...,argn_ are the function input values of interest.
Then the variable _res_ is the list of the return values of the function.

### Input granularity
You can fine tune how many inputs you want to dispatch to each process with the __inputs_per_worker__ argument.

If the computation time does not vary from input to input, than it is convenient to assign an equal amount of inputs to each process to not create process creation/destruction overhead.
If the computation time varies from input to input, you may want to assign few inputs per process so to avoid the chance of having one process particularly unlucky finishing after all the others.

The helper functions 
```
pll.stakanovs
pll.minions
```
assign to each process an equal amount of inputs and only one input respectively.

### Printing
The standard output of the processes can be redirected to a file.
```
import parallelism as pll

with open("myresults.data", "w") as outfile:
	res = pll.launch_workers([dict(arg=arg1), dict(arg=arg2), ...], 
							math_intensive_computation, parallelism=4,
							outfile=outfile)
```

## Tests
Run the following to test against the test-suite
```
python -mpytest 
```
