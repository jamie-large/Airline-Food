#!/usr/bin/env/python
# PDA-er interpreter
# Written by Jamie Large in March 2021
# Version 1.0
import sys

debug = True
lookup_table = dict()
stack = []
labels = []

def main():
	code = ""
	# Get the code, either as input from the user until they send EOF or from the specified file
	if (len(sys.argv) == 1):
		str_buf = []
		while True:
			buf = sys.stdin.readline()
			if not buf:
				break
			str_buf.append(buf)
		code = ''.join(str_buf)
	else:
		try:
			with open(sys.argv[1], 'r') as f:
				code = f.read()
		except:
			print('Error reading file: ' + sys.argv[1])

	global pointer 
	pointer = -1
	
	c = 0
	while True:
		if debug:
			print_stack()

		if (c >= len(code)):
			break

		# Add variable to stack
		if code[c:c+16] == "You ever notice " or code[c:c+21] == "What's the deal with ":
			c = c + 16 if code[c:c+16] == "You ever notice " else c + 21
			
			var_name = read_variable(code[c:], '?')
			if (var_name == -1): break

			if var_name in lookup_table:
				sys.exit("ERROR: Variable " + var_name + " already exists.")

			if var_name != "airline food":
				lookup_table[var_name] = len(stack)
			stack.append(1)

			if code[c-16:c] != "You ever notice ":
				pointer = len(stack) - 1

			c = c + len(var_name) + 2

			continue
		
		# Move pointer up the stack if possible
		if code[c:c+3] == "Um,":
			if pointer == -1:
				sys.exit("ERROR: Pointer uninitialized")
			if pointer < len(stack) - 1:
				pointer = pointer + 1
			c = c + 4
			continue

		# Move pointer down the stack if possible
		if code[c:c+5] == "Yeah,":
			if pointer == -1:
				sys.exit("ERROR: Pointer uninitialized")
			if pointer > 0:
				pointer = pointer - 1
			c = c + 6
			continue

		# Set the pointer
		if code[c:c+17] == "Let's talk about ":
			c = c + 17

			var_name = read_variable(code[c:], '.')
			if (var_name == -1): break

			if var_name not in lookup_table:
				sys.exit("ERROR: Variable " + var_name + " does not exist.")

			pointer = lookup_table[var_name]

			c = c + len(var_name) + 2
			continue

		# Add/subtract/multiply to the pointer's position
		if code[c:c+16] == "It's kinda like " or code[c:c+9] == "Not like " or code[c:c+10] == "Just like ":
			c = c + 16 if code[c:c+16] == "It's kinda like " else c + 9 if code[c:c+9] == "Not like " else c+10

			var_name = read_variable(code[c:], '.')
			if (var_name == -1): break

			if var_name not in lookup_table:
				sys.exit("ERROR: Variable " + var_name + " does not exist.")
			if pointer == -1:
				sys.exit("ERROR: Pointer uninitialized")

			if code[c-9:c] == "Not like ":
				stack[pointer] = stack[pointer] - stack[lookup_table[var_name]]
			elif code[c-10:c] == "Just like ":
				stack[pointer] = stack[pointer] * stack[lookup_table[var_name]]
			else:
				stack[pointer] = stack[pointer] + stack[lookup_table[var_name]]

			c = c + len(var_name) + 2
			continue

		# Add a label
		if code[c:c+5] == "So...":
			c = c+5
			labels.append(c)
			continue

		# Goto a label (or move past it) depending on value in the pointer
		if code[c:c+12] == "Moving on...":
			if pointer == -1:
				sys.exit("ERROR: Pointer uninitialized")
			if not labels:
				sys.exit("ERROR: No corresponding 'So...'")

			if stack[pointer] != 0:
				c = labels[-1]
			else:
				labels.pop()
				c = c+12
			continue

		# Input
		if code[c:c+6] == "Right?":
			if pointer == -1:
				sys.exit("ERROR: Pointer uninitialized")
			while True:
				try:
					x = int(input())
				except ValueError:
					print("Invalid input. Please enter an integer.")
				else:
					break
			stack[pointer] = x
			c = c+6
			continue

		# Output
		if code[c:c+4] == "See?":
			if pointer == -1:
				sys.exit("ERROR: Pointer uninitialized")
			if stack[pointer] <= 0x10FFFF and stack[pointer] >= 0 and not debug:
				print(chr(stack[pointer]), end='')
			else:
				print(str(stack[pointer]), end='')

			c = c+4
			continue

		
		c += 1



# Reads from code string until it encounters stop_char
# Returns -1 if it never encounters stop_char
def read_variable(code, stop_char):
	c = 0
	while (True):
		if (c == len(code)):
			return -1
		if (code[c] == stop_char):
			break
		c += 1

	return code[0:c]

# Prints the stack of variables (useful for debugging)
def print_stack():
	reverse_lookup_table = {v: k for k, v in lookup_table.items()}

	extra_str = reverse_lookup_table[pointer] if pointer in reverse_lookup_table else ""
	print("Pointer: " + str(pointer) + " (" + extra_str + ")")
	print("Labels: " + str(labels))
	print("STACK:")

	for i in range(len(stack)):
		if i in reverse_lookup_table:
			print(reverse_lookup_table[i] + ": " + str(stack[i]))
		else:
			print(str(i) + ": " + str(stack[i]))

	print

main()