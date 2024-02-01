from dataclasses import dataclass, field
from typing import Dict, Union

@dataclass
class Factor:
    value: str
    range: str = None

@dataclass
class UnitConversion:
    equation: str

@dataclass
class Calculation:
    detail: str

@dataclass
class Result:
    detail: Union[str, None] = None
    extra: Union[str, None] = None

@dataclass
class FermiData:
    Problem: str = ""
    Factors: dict[str, Factor] = field(default_factory=dict)
    UnitConversions: dict[str, UnitConversion] = field(default_factory=dict)
    UncertaintyType: str = ""
    Calculations: dict[str, Calculation] = field(default_factory=dict)
    Results: dict[str, Result] = field(default_factory=dict)

def parse_fermi_problem(file_path:str):
    fermi_data = FermiData()

    current_section = None

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            if line.startswith('Problem:') or line.startswith('Uncertainty Type:'):
                fermi_data.Problem = line.split(':', 1)[1].strip()

            elif line.startswith('---'):
                current_section = None

            elif ':' in line and current_section is not None:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if current_section == 'Factors':
                    if '[' in value and ']' in value:
                        value, value_range = value.split('[', 1)
                        value_range = value_range.strip(']')
                        value = value.strip()
                        fermi_data.Factors[key] = Factor(value, value_range)
                    else:
                        fermi_data.Factors[key] = Factor(value)
                elif current_section == 'Results':
                    if '[' in value and ']' in value:
                        value, value_range = value.split('[', 1)
                        value_range = value_range.strip(']')
                        value = value.strip()
                        fermi_data.Results[key] = Result(value, value_range)
                    else:
                        fermi_data.Results[key] = Result(value)
                elif current_section == 'UnitConversion':
                    fermi_data.UnitConversions[key] = UnitConversion(value)
                elif current_section == 'Calculations':
                    fermi_data.Calculations[key] = Calculation(value)
                elif current_section == 'Results':
                    fermi_data.Results[key] = Result(value)
                else:
                    raise ValueError(f"Can't place line: {line} for {current_section}")

            elif line in ['Factors', 'UnitConversion', 'Calculations', 'Results'] or line.startswith('UnitConversion:'):
                 current_section = line
            else:
                raise ValueError(f"Can't place line: {line}")
                # print(f"Can't place line: {line}")
        return fermi_data
# def parse_fermi_problem(file_path:str):
#     fermi_data = {
#         "Problem": "",
#         "Factors": {},
#         "UnitConversion": {},
#         "UncertaintyType": "",
#         "Calculations": {},
#         "Results": {}
#     }
#
#     current_section = None
#     problem_done = False
#     current_section = "Problem"
#     with open(file_path, 'r') as file:
#         for line in file:
#             line = line.strip()
#
#             if line.startswith('Problem:'):
#                 # TODO: support mutliple lines for problem
#                 fermi_data["Problem"] = line.split(':', 1)[1].strip()
#                 problem_done = True
#             elif line.startswith('---'):
#                 current_section = None
#
#             elif ':' in line and current_section is not None:
#                 key, value = line.split(':', 1)
#                 if current_section == 'Factors' or current_section == 'Results':
#                     # Handle range or distribution in brackets if present
#                     if '[' in value and ']' in value:
#                         value, extra = value.split('[', 1)
#                         extra = extra.strip(']')
#                         value = value.strip()
#                         fermi_data[current_section][key.strip()] = {'value': value, 'extra': extra}
#                     else:
#                         fermi_data[current_section][key.strip()] = value.strip()
#                 elif current_section == 'Calculations':
#                     # Specific parsing for calculations can be done here
#                     fermi_data[current_section][key.strip()] = value.strip()
#                 elif current_section == 'UnitConversion':
#                     fermi_data[current_section][key.strip()] = value.strip()
#
#             elif 'Uncertainty Type:' in line:
#                 fermi_data["UncertaintyType"] = line.split(':', 1)[1].strip()
#
#             elif line in ['Factors', 'UnitConversion', 'Calculations', 'Results']:
#                 current_section = line
#
#     return fermi_data

if __name__ == '__main__':
    # Usage
    file_path = '../files/piano.txt'
    parsed_data = parse_fermi_problem(file_path)
    print(parsed_data)