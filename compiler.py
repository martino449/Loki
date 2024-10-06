filepath: str = "main.loki"
in_main: bool = False
in_func: bool = False
flexible: bool = False
AMMS: bool = False
c_code: str = ""
variables = {}  
def extract_if_condition(input_str):
    return input_str.lower().split('if')[1].split('then')[0].strip().split() if 'if' in input_str and 'then' in input_str else []

def extract_while_condition(input_str):
    return input_str.lower().split('while')[1].split('do')[0].strip().split() if 'while' in input_str and 'do' in input_str else []


if AMMS:
    with open("./libs/AMMS.c", "r") as f:
        c_code += f.read()
with open(filepath, "r") as f:
    program_lines = [
        line.strip() for line in f.readlines()
    ]


get_type = {
    "int": "int",
    "float": "float",
    "string": "string",
    "bool": "bool",
    "nat": "unsigned int",
    "real": "long double",
    "rat": "double",
    "char": "char",
    "long": "long",
    "really_long": "long long",

}
c_code += "#include <stdio.h> \n"
print("Compilation in C started...")
for line in program_lines:
    parts = line.split(" ")
    opcode = parts[0]
    if in_main or in_func:
        opt = "\t"
    else:
        opt = ""
    match opcode:

        case _ if opcode in variables:
            c_code += opt + line + ";\n"
        
        case "pause":
            c_code += opt + "getchar();\n"
        case "out":
            # Checking if part[1] exists in the variables dictionary
            if parts[1] in variables:
                var_type = variables[parts[1]]
                var_name = parts[1]

                # Handling the output based on variable type
                if var_type == "str":
                    c_code += opt + f'printf("%s", {var_name}); \n'
                elif var_type == "char":
                    c_code += opt +  f'printf("%c", {var_name}); \n'
                elif var_type == "int":
                    c_code += opt + f'printf("%d", {var_name}); \n'
                elif var_type == "float":
                    c_code += opt + f'printf("%f", {var_name}); \n'
                else:
                    to_print = parts[1] if len(parts) > 1 else ""
                    c_code += opt + f'printf("{to_print}"); \n'


        case "start_main":
            c_code += "int main(void) {\n"
            in_main = True


        case "end_main":
            c_code += "\treturn 0;\n}\n"
            in_main = False

        case "var":
            var_value = ""
            var_type = parts[2]
            var_name = parts[1].replace(":", "")
            var_values_list = [valore for indice, valore in enumerate(parts) if indice > 3]
            for value in var_values_list:
                var_value += f" {value}"
            
            c_code += opt + f"{get_type[var_type]} {var_name} = {var_value};\n"
            variables[var_name] = var_type

        
        case "func":
            func_args = ""
            in_func = True
            func_type = parts[1]
            func_name = parts[2]
            args_list = []
            for indice, valore in enumerate(parts):
                if indice > 2:
                    args_list.append(valore)
            for arg in args_list:   
                func_args += f"{arg} "
            c_code += opt + f"{get_type[func_type]} {func_name}{func_args}" + "{\n"
        

        case "end":
            in_func = False
            c_code += "}\n"


        case "macro":
            macro_name = parts[1]
            macro_value = [valore for indice, valore in enumerate(parts) if indice > 2]
            c_code += f"#define {macro_name} {macro_value}\n"

        case "const":
            var_value = ""
            var_type = parts[1]
            var_name = parts[2]
            var_values_list = [valore for indice, valore in enumerate(parts) if indice > 3]
            for value in var_values_list:
                var_value += f" {value}"
            
            c_code += opt + f"const {get_type[var_type]} {var_name} = {var_value};\n"       


        case "if":
            condition_body = ""
            if_conditions = extract_if_condition(line)
            for cond in if_conditions: 
                condition_body += cond + " "
            condition_body = condition_body[:-1]

            c_code += opt + f"if ({condition_body})" + "{\n"
                
        case "else":
            c_code += opt + "}else {\n"
        
        case "while":
            condition_body = ""
            if_conditions = extract_while_condition(line)
            for cond in if_conditions: 
                condition_body += cond + " "
            condition_body = condition_body[:-1]

            c_code += opt + f"while ({condition_body})" + "{\n"

        case "return":
            c_code += opt + line + ";\n"

        case _:
            c_code += opt + line + ";\n"

            
            
print(c_code)
with open("out.c", "w") as f:
    f.write(c_code)