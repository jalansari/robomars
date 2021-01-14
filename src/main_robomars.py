from argparse import (ArgumentParser, ArgumentTypeError)

from src.instructionfile import (
    InstructionsFile,
    ExceptionFileParseCritical
)
from src.grid import Grid
from src.robot import Robot


class MainExec(object):

    class ParsedArgs(object):
        def __init__(self, infile):
            self.input_file = infile

    def buildArgParser(self):
        argParser = ArgumentParser(description='Robot instructions.')
        argParser.add_argument(
            'input_file', default=None,  # nargs=None,
            help='Path of file containing robot instructions.')
        parsed = argParser.parse_args()
        parsedArgs = MainExec.ParsedArgs(parsed.input_file)
        return parsedArgs

    def do_instructions(self, grid, robot, robot_instructions):
        for inst in robot_instructions.instruction_list:
            inst.do(grid, robot)
            if robot.is_lost:
                break

    def run_main(self):
        parsedargs = self.buildArgParser()
        input_file = parsedargs.input_file
        print(f'===== {input_file} =====')
        inst_file_processor = InstructionsFile(input_file)
        try:
            inst_file_processor.initialise_instructions()
            grid = Grid(inst_file_processor.grid_extents)
            for robot_instructions in inst_file_processor.next_instructions():
                robot = Robot()
                self.do_instructions(grid, robot, robot_instructions)
                print(str(robot))
            print()
        except ExceptionFileParseCritical as ex:
            print(ex)
            print(ex.path)
            if ex.line_num is not None:
                print(f'@{ex.line_num}: "{ex.line}"')
            print()
            exit(ex.code)
