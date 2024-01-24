from math import floor

from math import floor
import Tkinter as tk
import tkFileDialog  # Note: In Python 2, it's tkFileDialog, not filedialog
import tkMessageBox as messagebox

import hdlparse.verilog_parser as vlog
import re
import random
import os





#-------------------------------MODULE AS A CLASS---------------------------------------------#

class VerilogModule:
    def __init__(self, name):
        self.name = name
        self.ports = []
        self.BA = []
        self.NBA = []
        self.Logical = []
        self.Ifs = []
        self.cases = []
        self.clock = None
        self.reset = None
        self.clocked = False
        self.resettable = False
        self.caseattempts = []

    def add_port(self, name, mode, data_type, length):
        self.ports.append({
            "name": name,
            "mode": mode,
            "data_type": data_type,
            "length": length
        })
        if self.is_clock_input(name):
            self.clocked = True
            self.clock = name

        if self.is_reset_input(name):
            self.resettable = True
            self.reset = name

    def add_BA(self, lhs, operator, rhs):
        self.BA.append({
            "LHS": lhs,
            "OPERATOR": operator,
            "RHS": rhs
        })

    def add_NBA(self, lhs, operator, rhs):
        self.NBA.append({
            "LHS": lhs,
            "OPERATOR": operator,
            "RHS": rhs
        })

    def add_Logical_Member(self, member):

        # Remove the last 3 characters if they match the pattern "[%digit]"
        if re.search(r'\[\d\]$', member):
            member = member[:-3]

        if member not in ['&', '&&', '|', '||', '!', '~', '(', ')', '{', '}', '=', '<', '>', 'None', ';']:
            # Add to Logical only if it's not already present
            if member not in self.Logical:
                self.Logical.append(member)


    def add_Ifs(self, ifmember):
        self.Ifs.append({
            "IFMEMBERS": ifmember,
        })

    def add_Cases(self, cmember):
        self.cases.append({
            "CASEMEMBERS": cmember,
        })
    def add_caseattempt(self, owner, case):
        self.caseattempts.append({
            "OWNER": owner,
            "CASE": case,
        })

    def is_clock_input(self, name):
        return name.lower() == 'clock' or name.lower() == 'clk'

    def is_reset_input(self, name):
        return name.lower() == 'rst' or name.lower() == 'reset'

    def __str__(self):
        result = "Module: {}\nInputs:\n".format(self.name)
        for inp in self.ports:
            result += "\tName: {}, Mode: {}, Data Type: {}, Length: {}\n".format(
                inp['name'], inp['mode'], inp['data_type'], inp['length']
            )
        result += "Clocked: {}\n".format(self.clocked)
        result += "Resettable: {}\n".format(self.resettable)

        result += "BAs ----------------------------- \n"
        for BAs in self.BA:
            result += "\tLHS: {}, OPERATOR: {}, RHS: {}".format(
                BAs['LHS'], BAs['OPERATOR'], BAs['RHS']
            )
            result += "\n"

        result += "NBAs ---------------------------- \n"
        for NBAs in self.NBA:
            result += "\tLHS: {}, OPERATOR: {}, RHS: {}".format(
                NBAs['LHS'], NBAs['OPERATOR'], NBAs['RHS']
            )
            result += "\n"

        result += "LOGICALS ---------------------------- \n"
        for Lg in self.Logical:
            result += "\tMEMBER: {}".format(Lg)
            result += "\n"


        result += "IF STATMENTS ---------------------------- \n"
        for ifs in self.Ifs:
            result += "\tMEMBERS: {}".format(
                ifs['IFMEMBERS']
            )
            result += "\n"

        result += "CASE STATMENTS ---------------------------- \n"
        for cs in self.cases:
            result += "\tMEMBERS: {}".format(
                cs['CASEMEMBERS']
            )
            result += "\n"

        result += "SINGLE CASE VALUES ---------------------------- \n"
        for CAs in self.caseattempts:
            result += "\tOWNER: {}, CASE: {}".format(
                CAs['OWNER'], CAs['CASE']
            )
            result += "\n"

        return result








#-----------------------------------PARSING--------------------------------------------------#




def parse_if_statements(module_body, verilog_module):
    # Extract if statements using regular expressions
    if_matches = re.finditer(r'\bif\s*\((.*?)\)[^;]*', module_body, re.DOTALL)

    for if_match in if_matches:
        condition = if_match.group(1).strip()
        members = [member.strip() for member in re.findall(r'\b[a-zA-Z_]\w*\b', condition) if
                   member not in {'&', '&&', '|', '||', '!', '~', '(', ')', '{', '}', '=', '<', '>', None, ';', '+',
                                  '-', '*', '/', '%', '^', ',', '.', ':', '[', ']', '?', '@', '#', '$', '_', "<=", ">=",
                                  "=>", "=<", "==", "==="}]
        verilog_module.add_Ifs(members)



def parse_case_statements(module_body, verilog_module):
    # Extract case statements using regular expressions
    case_matches = re.finditer(r'\bcase\s*\((.*?)\)(.*?)\bendcase\b', module_body, re.DOTALL)

    for case_match in case_matches:
        condition = case_match.group(1).strip()
        members = [member.strip() for member in re.findall(r'\b[a-zA-Z_]\w*\b', condition) if
                   member not in {'&', '&&', '|', '||', '!', '~', '(', ')', '{', '}', '=', '<', '>', None, ';', '+',
                                  '-', '*', '/', '%', '^', ',', '.', ':', '[', ']', '?', '@', '#', '$', '_', "<=", ">=",
                                  "=>", "=<", "==", "==="}]
        verilog_module.add_Cases(members)

        # Check if there's only one member in the condition
        if len(members) == 1:
            case_body = case_match.group(2)
            owner = members[0]
            parse_case_attempts(owner, case_body, verilog_module)


def parse_case_attempts(owner, case_body, verilog_module):
    # Extract case attempts using regular expressions
    case_attempt_matches = re.finditer(r'(\d+\'b[01]+)\s*:', case_body)

    for case_attempt_match in case_attempt_matches:
        full_case_specifier = case_attempt_match.group(1)
        verilog_module.add_caseattempt(owner, full_case_specifier)




def parse_logical_equations(line, verilog_module):
    def is_operator(char):
        return char in {'&', '|', '!', '~', '==', '!=', '>', '<', '>=', '<=', '^'}

    def extract_operands(expression, operator, characters_to_exclude):
        inside_parentheses = expression[expression.index('(') + 1:expression.rindex(')')] if '(' in expression and ')' in expression else expression
        operands = [m.strip() for m in inside_parentheses.split(operator) if not any(char in m for char in characters_to_exclude)]
        return operands

    characters_to_exclude = {'(', ')', '{', '}', '=', '<', '>', ';', '+', '-', '*', '/', '%', '^', ',', '.', ':', '?', '@', '#', '$', '_', "<=", ">=", "=>", "=<", '&&', '||', '\''}

    words = line.split()
    i = 0
    while i < len(words):
        word = words[i]
        if is_operator(word):
            # Unary operator
            if len(word) == 1:
                operand = words[i + 1].strip('();,')
                verilog_module.add_Logical_Member(operand)
                i += 1  # Skip the next word
            # Binary operator
            else:
                operands = extract_operands(words[i + 1], word, characters_to_exclude)
                for operand in operands:
                    verilog_module.add_Logical_Member(operand)
                i += 1  # Skip the next word(s)
        i += 1

def parse_assignment_blocking(verilog_code, verilog_module):
    assignments = []

    lines = verilog_code.split('\n')

    for line in lines:
        # Find the '=' operator in the line
        equal_index = line.find('=')

        if equal_index != -1:
            # Extract LHS
            lhs = line[:equal_index].rstrip().split()[-1]

            # Check for conditions to skip the assignment
            if any(char in lhs.strip() for char in ['!', '<', '>', '=']):
                continue

            # Check for symbols before and after '='
            if equal_index > 0 and line[equal_index - 1] in ['!', '<', '=', '>']:
                continue
            if equal_index < len(line) - 1 and line[equal_index + 1] in ['=', '>']:
                continue

            # Extract RHS
            rhs_start_index = equal_index + 1
            rhs_end_index = line.find(';', rhs_start_index)
            rhs = line[rhs_start_index:rhs_end_index].lstrip().rstrip()

            # Create assignment dictionary
            assignment = {
                'OPERATOR': '=',
                'LHS': lhs,
                'RHS': rhs
            }

            # Add assignment to the list
            assignments.append(assignment)

    # Update the VerilogModule instance with the parsed assignments
    for assignment in assignments:
        verilog_module.add_BA(assignment['LHS'], assignment['OPERATOR'], assignment['RHS'])


def parse_assignment_non_blocking(verilog_code, verilog_module):
    assignments = []

    lines = verilog_code.split('\n')

    for line in lines:
        # Find the '<=' operator in the line
        nba_index = line.find('<=')

        if nba_index != -1:
            # Extract LHS
            lhs_end_index = nba_index - 1
            while lhs_end_index >= 0 and line[lhs_end_index].isspace():
                lhs_end_index -= 1
            while lhs_end_index >= 0 and not line[lhs_end_index].isspace():
                lhs_end_index -= 1
            lhs = line[lhs_end_index + 1:nba_index].rstrip()

            # Extract RHS
            rhs_start_index = nba_index + 2
            rhs_end_index = line.find(';', rhs_start_index)
            if rhs_end_index == -1:
                # Check for comments after ';'
                comment_start_index = line.find('//', rhs_start_index)
                if comment_start_index != -1:
                    rhs = line[rhs_start_index:comment_start_index].lstrip().rstrip()
                else:
                    rhs = line[rhs_start_index:].lstrip().rstrip()
            else:
                rhs = line[rhs_start_index:rhs_end_index].lstrip().rstrip()

            # Create assignment dictionary
            assignment = {
                'OPERATOR': '<=',
                'LHS': lhs,
                'RHS': rhs
            }

            # Add assignment to the list
            assignments.append(assignment)

    # Update the VerilogModule instance with the parsed assignments
    for assignment in assignments:
        # Skip assignments with empty LHS or RHS
        if assignment['LHS'] and assignment['RHS']:
            verilog_module.add_NBA(assignment['LHS'], assignment['OPERATOR'], assignment['RHS'])


def vector_size(line):
    if re.search(r'\[', line):
        lval = re.findall(r'\[(.*):', line)[0]
        rval = re.findall(r'\[.*:(.*)\]', line)[0]
        return abs(int(rval) - int(lval)) + 1
    return 1

def parse_module_inputs_and_outputs(module, ports):
    for p in ports:

        data_type_split = p.data_type.split()
        print data_type_split
        d_t = "wire"
        v_s = 1

        if any("reg" in dtype for dtype in data_type_split):
            d_t = "reg"
        if any("[" in dtype for dtype in data_type_split):
            # Find the index of the element containing "[" and get its vector size
            index_with_bracket = next((i for i, dtype in enumerate(data_type_split) if "[" in dtype), None)
            if index_with_bracket is not None:
                v_s = vector_size(data_type_split[index_with_bracket])


        module.add_port(
            name=p.name,
            mode=p.mode,
            data_type=d_t,
            length=v_s
        )





###-------------------------MAIN TESTBENCH GENERATION----------------------------------###

def generate_Logical_test(tb_file, module, standard_delay, num_random_values=5):
    if module.Logical:
        tb_file.write("\t//======================================================\n")
        tb_file.write("\t// Logical Test\n")
        tb_file.write("\t//======================================================\n")

        tb_file.write("\n$display(\"----------LOGICAL OPERATOR TESTS----------\");")

        tested_members = set()  # Use a set for faster membership tests

        for logical_member in module.Logical:
            # Check if logical_member is an input port
            matching_ports = [port for port in module.ports if port["mode"].lower() == "input" and port["name"] == logical_member]

            if matching_ports:
                port_name = matching_ports[0]["name"]
                port_length = matching_ports[0]["length"]

                # Check if the port is already tested
                if port_name not in tested_members:
                    tb_file.write("\t// Logical Test for Member: {}\n".format(logical_member))

                    # Randomize a subset of values for the port
                    random_values = random.sample(range(2 ** port_length), min(num_random_values, 2 ** port_length))

                    for value in random_values:
                        tb_file.write("\t{} = {};\n".format(port_name, "{0}'b{1:0{0}b}".format(port_length, value)))

                        # Add delay
                        tb_file.write("\t#{}\n".format(standard_delay))

                    # Toggle reset if resettable
                    if module.resettable:
                        tb_file.write("\t{} = 1;\n".format(module.reset))
                        tb_file.write("\t#{}\n".format(standard_delay))
                        tb_file.write("\t{} = 0;\n".format(module.reset))
                        tb_file.write("\t#{}\n".format(standard_delay))

                    # Add delay
                    tb_file.write("\t#{}\n".format(standard_delay))

                    # Add the port to the tested set
                    tested_members.add(port_name)

        tb_file.write("\t//======================================================\n")

def generate_ba_test(tb_file, module, standard_delay, num_random_values=5):
    if module.BA:
        tb_file.write("\t//======================================================\n")
        tb_file.write("\t// BAs Test\n")
        tb_file.write("\t//======================================================\n")
        tb_file.write("\n$display(\"----------BLOCKING ASSIGNMENT TESTS----------\");")



        tested_ports = set()  # Use a set for faster membership tests

        for ba in module.BA:
            lhs = ba['LHS']
            rhs = ba['RHS']

            # Check if RHS contains input ports
            matching_ports = [port for port in module.ports if port["mode"].lower() == "input" and port["name"] in rhs]

            if matching_ports:
                # Loop over a random subset of values for each matching input port
                for port in matching_ports:
                    port_name = port["name"]
                    port_length = port["length"]

                    # Check if the port is already tested
                    if port_name not in tested_ports:
                        tb_file.write("\t// BA Test for RHS: {}\n".format(rhs))

                        # Randomize a subset of values for the port
                        random_values = random.sample(range(2 ** port_length), min(num_random_values, 2 ** port_length))

                        for value in random_values:
                            tb_file.write("\t{} = {};\n".format(port_name, "{0}'b{1:0{0}b}".format(port_length, value)))

                            # Add delay
                            tb_file.write("\t#{}\n".format(standard_delay))

                        # Toggle reset if resettable
                        if module.resettable:
                            tb_file.write("\t{} = 1;\n".format(module.reset))
                            tb_file.write("\t#{}\n".format(standard_delay))
                            tb_file.write("\t{} = 0;\n".format(module.reset))
                            tb_file.write("\t#{}\n".format(standard_delay))

                        # Add delay
                        tb_file.write("\t#{}\n".format(standard_delay))

                        # Add the port to the tested set
                        tested_ports.add(port_name)

        tb_file.write("\t//======================================================\n")


def generate_nba_test(tb_file, module, standard_delay, num_random_values=5):
    if module.NBA:
        tb_file.write("\t//======================================================\n")
        tb_file.write("\t// NBAs Test\n")
        tb_file.write("\t//======================================================\n")
        tb_file.write("\n$display(\"----------NON BLOCKING ASSIGNMENT TESTS----------\");")

        tested_ports = set()  # Use a set for faster membership tests

        for nba in module.NBA:
            lhs = nba['LHS']
            rhs = nba['RHS']

            # Check if RHS contains input ports
            matching_ports = [port for port in module.ports if port["mode"].lower() == "input" and port["name"] in rhs]

            if matching_ports:
                # Loop over a random subset of values for each matching input port
                for port in matching_ports:
                    port_name = port["name"]
                    port_length = port["length"]

                    # Check if the port is already tested
                    if port_name not in tested_ports:
                        tb_file.write("\t// NBA Test for RHS: {}\n".format(rhs))

                        # Randomize a subset of values for the port
                        random_values = random.sample(range(2 ** port_length), min(num_random_values, 2 ** port_length))

                        for value in random_values:
                            tb_file.write("\t{} = {};\n".format(port_name, "{0}'b{1:0{0}b}".format(port_length, value)))

                            # Add delay
                            tb_file.write("\t#{}\n".format(standard_delay))

                        # Toggle reset if resettable
                        if module.resettable:
                            tb_file.write("\t{} = 1;\n".format(module.reset))
                            tb_file.write("\t#{}\n".format(standard_delay))
                            tb_file.write("\t{} = 0;\n".format(module.reset))
                            tb_file.write("\t#{}\n".format(standard_delay))

                        # Add delay
                        tb_file.write("\t#{}\n".format(standard_delay))

                        # Add the port to the tested set
                        tested_ports.add(port_name)

        tb_file.write("\t//======================================================\n")




def generate_case_test(tb_file, module, standard_delay, num_random_values=5):
    if module.cases or module.caseattempts:
        tb_file.write("\t//======================================================\n")
        tb_file.write("\t// Random and Specific Case Test\n")
        tb_file.write("\t//======================================================\n")
        tb_file.write("\n$display(\"----------RANDOM CASE TESTS----------\");")

        tested_ports = set()  # Use a set for faster membership tests

        # Generate test cases for cases
        for case in module.cases:
            casemembers = case['CASEMEMBERS']

            # Check if casemembers contain input ports
            matching_ports = [port for port in module.ports if port["mode"].lower() == "input" and port["name"] in casemembers]

            if matching_ports:
                # Loop over a random subset of values for each matching input port
                for port in matching_ports:
                    port_name = port["name"]
                    port_length = port["length"]

                    # Check if the port is already tested
                    if port_name not in tested_ports:
                        tb_file.write("\t// Case Test for CASEMEMBERS: {}\n".format(casemembers))

                        # Generate random values
                        random_values = [
                            "{0}'b{1:0{0}b}".format(port_length, random.randint(0, 2 ** port_length - 1))
                            for _ in range(min(num_random_values, 2 ** port_length + 1))
                        ]

                        # Loop over random values and binary digits
                        for value in random_values:
                            # Use blocking assignment to set the port to a random value
                            tb_file.write("\t{} = {};\n".format(port_name, value))

                            # Add delay
                            tb_file.write("\t#{};\n".format(standard_delay))

                        # Toggle reset if resettable
                        if module.resettable:
                            tb_file.write("\t{} = 1;\n".format(module.reset))
                            tb_file.write("\t#{}\n".format(standard_delay))
                            tb_file.write("\t{} = 0;\n".format(module.reset))
                            tb_file.write("\t#{}\n".format(standard_delay))

                        # Add delay
                        tb_file.write("\t#{};\n".format(standard_delay))

                        # Add the port to the tested set
                        tested_ports.add(port_name)


        # Generate test cases for case attempts
        tb_file.write("\n$display(\"----------SPECIFIC CASE TESTS----------\");")
        for caseattempt in module.caseattempts:
            owner = caseattempt['OWNER']
            case = caseattempt['CASE']

            # Check if owner contains input ports
            matching_ports = [port for port in module.ports if port["mode"].lower() == "input" and port["name"] == owner]

            if matching_ports:
                tb_file.write("\t// Case Attempt Test for OWNER: {}, CASE: {}\n".format(owner, case))

                # Set the owner to the case
                tb_file.write("\t{} = {};\n".format(owner, case))

                # Add delay
                tb_file.write("\t#{};\n".format(standard_delay))

                # Toggle reset if resettable
                if module.resettable:
                    tb_file.write("\t{} = 1;\n".format(module.reset))
                    tb_file.write("\t#{}\n".format(standard_delay))
                    tb_file.write("\t{} = 0;\n".format(module.reset))
                    tb_file.write("\t#{}\n".format(standard_delay))

                # Add delay
                tb_file.write("\t#{};\n".format(standard_delay))

        tb_file.write("\t//======================================================\n")

def generate_if_test(tb_file, module, standard_delay, num_random_values=5):
    if module.Ifs:
        tb_file.write("\t//======================================================\n")
        tb_file.write("\t// If Statements Test\n")
        tb_file.write("\t//======================================================\n")
        tb_file.write("\n$display(\"----------IF TESTS----------\");")

        tested_ports = set()  # Use a set for faster membership tests

        for if_statement in module.Ifs:
            ifmembers = if_statement.get('IFMEMBERS', [])

            # Check if ifmembers contain input ports
            matching_ports = [port for port in module.ports if port["mode"].lower() == "input" and port["name"] in ifmembers]

            if matching_ports:
                # Loop over a random subset of values for each matching input port
                for port in matching_ports:
                    port_name = port["name"]
                    port_length = port["length"]

                    # Check if the port is already tested
                    if port_name not in tested_ports:
                        tb_file.write("\t// If Statement Test for IFMEMBERS: {}\n".format(ifmembers))

                        # Randomize a subset of values for the port
                        random_values = random.sample(range(2 ** port_length), min(num_random_values, 2 ** port_length))

                        for value in random_values:
                            tb_file.write("\t{} = {};\n".format(port_name, "{0}'b{1:0{0}b}".format(port_length, value)))

                            # Add delay
                            tb_file.write("\t#{}\n".format(standard_delay))

                        # Toggle reset if resettable
                        if module.resettable:
                            tb_file.write("\t{} = 1;\n".format(module.reset))
                            tb_file.write("\t#{}\n".format(standard_delay))
                            tb_file.write("\t{} = 0;\n".format(module.reset))
                            tb_file.write("\t#{}\n".format(standard_delay))

                        # Add delay
                        tb_file.write("\t#{}\n".format(standard_delay))

                        # Add the port to the tested set
                        tested_ports.add(port_name)

        tb_file.write("\t//======================================================\n")

def generate_random_test_loop(tb_file, module, standard_delay, loop_iterations):
    if module.ports:
        tb_file.write("\t//======================================================\n")
        tb_file.write("\t// Random Test Loop\n")
        tb_file.write("\t//======================================================\n")
        tb_file.write("\n$display(\"----------FULLY RANDOM TEST LOOP----------\");")

        # Declare the loop variable outside the loop


        randomstring = "{$random}"
        # Print the for loop

        tb_file.write("\t\tfor (i = 0; i < {} ; i = i + 1) begin\n".format(loop_iterations))

        for port in module.ports:
            if port["mode"].lower() == "input" and port["name"] != module.clock:
                port_name = port["name"]
                port_length = port["length"]
                port_max = 2**port_length

                # Use $urandom_range to generate a random value for each iteration
                tb_file.write("\t\t\t{} = {} % {};\n".format(port_name,randomstring, port_max))

                # Add delay
                tb_file.write("\t\t\t#{};\n".format(standard_delay))

        # Toggle reset if resettable

        tb_file.write("\t\tend\n")


def generate_monitor_block(tb_file, module, standard_delay):
    if module.ports:
        tb_file.write("\t//======================================================\n")
        tb_file.write("\t// Monitor Block\n")
        tb_file.write("\t//======================================================\n")

        # Print the initial block
        tb_file.write("\tinitial begin\n")
        tb_file.write("\t\t$monitor(\"Time = %0t")

        outputs = []

        for port in module.ports:
            if port["mode"].lower() == "output":
                outputs.append(port)

        for port in outputs:
            tb_file.write(" {} = %b".format(port["name"]))

        tb_file.write("\", $time ")

        for port in outputs:
            tb_file.write(", {}".format(port["name"]))

        tb_file.write(");")


        # Print the end of the initial block
        tb_file.write("\tend\n\n")



def generate_testbench(timescale, clock_period, standard_delay, modules, loops):
    clock_period_half_cycle = str(clock_period // 2)

    for module in modules:
        # Add timescale definition
        timescale_line = "`timescale {}\n\n".format(timescale)
        start_module = "module {};\n\n".format(module.name + "_tb")
        end_module = "endmodule"

        # Create a new testbench file for the module
        save_path = choose_save_location(module.name)
        with open(save_path, 'w') as tb_file:
            tb_file.write(timescale_line)
            tb_file.write("\n\n")
            tb_file.write(start_module)

            for port in module.ports:
                # Check if it's an input
                if port["mode"].lower() == "input":
                    if port["length"] == 1:
                        tb_file.write("\treg {};\n".format(port["name"]))
                    else:
                        tb_file.write("\treg [{}:0] {};\n".format(port["length"] - 1, port["name"]))
                # Check if it's an output
                elif port["mode"].lower() == "output":
                    if port["length"] == 1:
                        tb_file.write("\twire {};\n".format(port["name"]))
                    else:
                        tb_file.write("\twire [{}:0] {};\n".format(port["length"] - 1, port["name"]))

            # Add module instantiation
            tb_file.write("{} {}_tb (\n".format(module.name, module.name))

            # Connect module ports
            for port in module.ports:
                tb_file.write("\t.{}({}),\n".format(port['name'], port['name']))

            #backspace once here
            tb_file.seek(-3, os.SEEK_END)
            tb_file.truncate()
            tb_file.write("\n")
            tb_file.write(");\n\n")

            tb_file.write("\n\n\tinteger i;\n\n")

            # Add clock generation if the module is clocked
            if module.clocked:
                tb_file.write("initial begin\n")
                tb_file.write("\t{module_name} = 0;\n".format(module_name=module.clock))
                tb_file.write("\tforever begin #{} {module_name} = ~{module_name};\n".format(clock_period_half_cycle, module_name=module.clock))
                tb_file.write("end\nend\n")

            # Add initial block
            tb_file.write("initial begin\n")
            tb_file.write("\t#{} // Initial delay\n".format(standard_delay))

            #--------------------------------------DIRECTED TESTING STARTS HERE---------------------------------#

            # Generate BA Test
            generate_ba_test(tb_file, module, standard_delay)

            #Generate NBA Test
            generate_nba_test(tb_file, module, standard_delay)

            #Generate case test
            generate_case_test(tb_file, module, standard_delay)

            #Generate if test
            generate_if_test(tb_file, module, standard_delay)

            #Generate logical test
            generate_Logical_test(tb_file, module, standard_delay)
            #------------------------------END DIRECTED TESTING ----------------------------------------------#

            #-------------------------------RANDOM TESTING STARTS HERE----------------------------------------#
            generate_random_test_loop(tb_file, module, standard_delay, loops)

            #--------------------------------END RANDOM TESTING----------------------------------------------#

            tb_file.write("$stop;\n")
            tb_file.write("end\n")

            generate_monitor_block(tb_file, module, standard_delay)

            tb_file.write(end_module)

        print("Testbench generated for module '{}' in file: {}".format(module.name, save_path))







def choose_file():
    root = tk.Tk()
    root.withdraw()

    # Ask user to choose input file
    input_path = os.path.normpath(tkFileDialog.askopenfilename(title="Choose your verilog file", filetypes=[("Text Files", "*.txt")]))

    return input_path

def choose_save_location(module_name):
    root = tk.Tk()
    root.withdraw()

    # Ask user to choose input file
    file_path = os.path.normpath(tkFileDialog.asksaveasfilename(title="Where to save the test bench", filetypes=[("Verilog Files", "*.v")]))
    if not file_path.endswith(".v"):
        file_path += ".v"

    return file_path
# ---------------------------------------MAIN----------------------------------------------------------#


def main():


    #LOAD THE FILE
    messagebox.showwarning("Warning", "Enter verilog file path, please make sure your verilog module compiles first: ")

    file_path = tkFileDialog.askopenfilename(
        title="Select Verilog File",
        filetypes=[("Verilog Files", "*.v"), ("All Files", "*.*")]
    )

    if file_path:
        messagebox.showwarning("File Selected", "Selected Verilog file: {}".format(file_path))
    else:
        messagebox.showwarning("Warning", "No file selected.")
        exit(-1)


    with open(file_path, 'rt') as fh:
        verilog_code = fh.read()

    vlog_ex = vlog.VerilogExtractor() #LIBRARY FOR EXTRACTING MODULES
    vlog_mods = vlog_ex.extract_objects_from_source(verilog_code)

    modules = [] #ARRAY OF MODULES EXTRACTED FROM FILE


    #MODULE PARSING
    for m in vlog_mods:
        current_module = VerilogModule(m.name)

        # Find the index of the module in the Verilog code
        start_index = verilog_code.find("module " + m.name)
        end_index = verilog_code.find("endmodule", start_index)

        # Extract the body of the module
        module_body = verilog_code[start_index:end_index + 10]  # module body so we don't pass the entire body for each module

        # Parse inputs and outputs
        parse_module_inputs_and_outputs(current_module, m.ports)

        # Parse blocking assignments
        parse_assignment_blocking(module_body, current_module)

        # Parse non-blocking assignments
        parse_assignment_non_blocking(module_body, current_module)

        # Parse Logical statements
        parse_logical_equations(module_body, current_module)

        # Parse ifs
        parse_if_statements(module_body, current_module)

        # Parse cases
        parse_case_statements(module_body, current_module)


        modules.append(current_module)

    # PRINT PARSED MODULES  --DEBUG
    for m in modules:
        print (m)

    # ASK USER FOR TB INFORMATION
    timescale = raw_input("Enter timescale (e.g., '1ns/1ps'): ")
    clock_period = input("Enter clock period (e.g., 10): ")
    standard_delay = input("Enter standard delay (e.g., 1): ")
    loops = input("Enter loop iteration count (e.g 1000000): ")




    # testbench
    generate_testbench(timescale, clock_period, standard_delay, modules, loops)





if __name__ == "__main__":
    main()
