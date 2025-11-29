from engineering_notation import EngUnit

from fermi_problems.files import parse_fermi_problem

file_path = "../files/piano.txt"
parsed_data = parse_fermi_problem(file_path)
print(parsed_data)

accumulator = None
for key, value in parsed_data.Factors.items():
    # number_part, unit_part = value.split(' ')
    print(key, EngUnit(value.value))
    if accumulator is None:
        accumulator = EngUnit(value.value)
    else:
        accumulator *= EngUnit(value.value)
print(accumulator)
