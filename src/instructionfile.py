import os
import re

from src.location import (
    Pos,
    Orientation,
    Label
)
from src.grid import Grid
from src.robot import Robot


ERROR_MSG_FILE_NOT_FOUND = 'ERROR - File not found.'
ERROR_MSG_NOT_A_FILE = 'ERROR - Not a file.'
ERROR_MSG_MISSING_GRID_MAX = 'ERROR - Missing grid extents.'
ERROR_MSG_ROBOT_POSITION_AND_DIRECTION_NOT_RECOGNISED = 'ERROR - robot position and direction not recognised.'
ERROR_MSG_ROBOT_INSTRUCTIONS_NOT_RECOGNISED = 'ERROR - robot instructions not recognised.'
ERROR_MSG_ROBOT_INSTRUCTIONS_MISSING = 'ERROR - robot instructions missing.'


class ExceptionFileParseCritical(Exception):

    # These can be used as exit codes, so must be greater than 1 to indicate an error.
    CODE_NOT_FOUND = 1
    CODE_NOT_FILE = 2
    CODE_MISSING_GRID_MAX = 3

    CODE_ROBOT_POSITION_AND_DIRECTION_NOT_RECOGNISED = 100
    CODE_ROBOT_INSTRUCTIONS_NOT_RECOGNISED = 101
    CODE_ROBOT_INSTRUCTIONS_MISSING = 102

    def __init__(self, code, message, path, line_num=None, line=None):
        super().__init__(message)
        self.code = code
        self.path = path
        self.line_num = line_num
        self.line = line


class Operation(object):
    def do(self, grid: Grid, robot: Robot):
        raise NotImplemented()

    def __repr__(self):
        return f'::{type(self).__name__}'


class Start(Operation):
    def __init__(self, pos: Pos, orientation: Orientation):
        self.pos = pos
        self.orientation = orientation

    def do(self, grid: Grid, robot: Robot):
        robot.set_state(self.pos, self.orientation)
        if not grid.is_within_grid(robot.position):
            robot.is_now_lost()

    def __repr__(self):
        return super().__repr__()+f'[{self.pos.coord_x},{self.pos.coord_y},{self.orientation.get_orientation()}]'


class TurnRight(Operation):
    def do(self, _: Grid, robot: Robot):
        robot.set_orientation(robot.orientation.new_orientation_90_clockwise())


class TurnLeft(Operation):
    def do(self, _: Grid, robot: Robot):
        robot.set_orientation(robot.orientation.new_orientation_90_anticlockwise())


class MoveForward(Operation):

    def __to_dropoff(grid, pos, orientation):
        label = grid.get_scent(pos)
        return label and label.is_next_drop(orientation)

    def do(self, grid: Grid, robot: Robot):
        if robot.is_lost:
            raise Exception('Dead')
        orientation = robot.orientation
        current_pos = robot.position
        # Ignore instruction if known bad place.
        if MoveForward.__to_dropoff(grid, current_pos, orientation):
            return
        next_position = orientation.next_forward_position(current_pos)
        if grid.is_within_grid(next_position):
            robot.set_position(next_position)
        else:
            robot.is_now_lost()
            label = Label(orientation)
            grid.add_scent(current_pos, label)


class Instructions(object):
    Instructions_Available = {
        'R': TurnRight,
        'L': TurnLeft,
        'F': MoveForward
    }

    def __init__(self, instruction_list):
        self.instruction_list = instruction_list

    def get_instructions_keys():
        return Instructions.Instructions_Available.keys()

    def create_instruction(ch):
        op = None
        OpClass = Instructions.Instructions_Available.get(ch)
        if OpClass:
            op = OpClass()
        return op

    def __str__(self):
        retstring = ''
        for inst in self.instruction_list:
            retstring += f'{str(inst)} '
        if retstring:
            retstring = retstring[:-1]
        return retstring


class InstructionsFile(object):

    RE_POSITION = r'\s*(\d+)\s+(\d+)\s*'
    RE_Grid_Max = re.compile(r'^'+RE_POSITION+r'$')
    RE_Start_State = re.compile(r'^'+RE_POSITION+r'\s([NSEW])\s*$')

    def __init__(self, path):
        self.file_path = path
        self.file = None
        self.file_line_num = 0
        self.__grid_extents = None
        self.is_EOF = False

    @property
    def grid_extents(self):
        return self.__grid_extents

    def __open_file(self):
        try:
            self.file = open(self.file_path, "r")
        except IsADirectoryError:
            raise ExceptionFileParseCritical(
                ExceptionFileParseCritical.CODE_NOT_FILE, ERROR_MSG_NOT_A_FILE,
                self.file_path)
        except FileNotFoundError:
            raise ExceptionFileParseCritical(
                ExceptionFileParseCritical.CODE_NOT_FOUND, ERROR_MSG_FILE_NOT_FOUND,
                self.file_path)

    def __read_next_line_from_file(self):
        next_line = self.file.readline()
        if not next_line:
            self.is_EOF = True
        else:
            self.file_line_num += 1
            next_line = next_line.strip('\n')
        return next_line

    def __set_grid_extents(self, gridext_line):
        match = InstructionsFile.RE_Grid_Max.match(gridext_line)
        if match is None:
            raise ExceptionFileParseCritical(
                ExceptionFileParseCritical.CODE_MISSING_GRID_MAX, ERROR_MSG_MISSING_GRID_MAX,
                self.file_path, self.file_line_num, gridext_line)
        self.__grid_extents = Pos(int(match[1]), int(match[2]))

    def __look_ahead_for_next_line(self):
        look_ahead_line = self.__read_next_line_from_file()
        while not self.is_EOF and not look_ahead_line:
            look_ahead_line = self.__read_next_line_from_file()
        return look_ahead_line

    def __next_line_raise_if_missing_instructions(self, next_instruction_expected=False):
        line = self.__read_next_line_from_file()
        if not line:
            if next_instruction_expected:
                line = self.__look_ahead_for_next_line()
            else:
                raise ExceptionFileParseCritical(
                    ExceptionFileParseCritical.CODE_ROBOT_INSTRUCTIONS_MISSING, ERROR_MSG_ROBOT_INSTRUCTIONS_MISSING,
                    self.file_path, self.file_line_num, line)
        return line

    def __first_ever_line_of_instructions_or_raise(self):
        line = self.__read_next_line_from_file()
        if not line:
            line = self.__look_ahead_for_next_line()
        if not line:
            raise ExceptionFileParseCritical(
                ExceptionFileParseCritical.CODE_ROBOT_INSTRUCTIONS_MISSING, ERROR_MSG_ROBOT_INSTRUCTIONS_MISSING,
                self.file_path, self.file_line_num, line)
        return line

    def __make_start_position_or_raise(self, line_one):
        match = InstructionsFile.RE_Start_State.match(line_one)
        if match is None:
            raise ExceptionFileParseCritical(
                ExceptionFileParseCritical.CODE_ROBOT_POSITION_AND_DIRECTION_NOT_RECOGNISED, ERROR_MSG_ROBOT_POSITION_AND_DIRECTION_NOT_RECOGNISED,
                self.file_path, self.file_line_num, line_one)
        pos = Pos(int(match[1]), int(match[2]))
        direction_char = match[3]
        direction = Orientation(direction_char)
        return (pos, direction)

    def __make_instructions_list(self, start_pos, start_direction, instructions_string):
        instructions_list = []
        start_state = Start(start_pos, start_direction)
        instructions_list.append(start_state)
        for idx, a_char in enumerate(instructions_string):
            if a_char not in Instructions.get_instructions_keys():
                raise ExceptionFileParseCritical(
                    ExceptionFileParseCritical.CODE_ROBOT_INSTRUCTIONS_NOT_RECOGNISED, ERROR_MSG_ROBOT_INSTRUCTIONS_NOT_RECOGNISED,
                    self.file_path, self.file_line_num, f'Character "{a_char}" at position {idx}')
            an_inst = Instructions.create_instruction(a_char)
            instructions_list.append(an_inst)
        return instructions_list

    def initialise_instructions(self):
        self.__open_file()
        first_line = self.__read_next_line_from_file()
        self.__set_grid_extents(first_line)

    def next_instructions(self):
        line_one = self.__first_ever_line_of_instructions_or_raise()
        while line_one:
            (pos, direction) = self.__make_start_position_or_raise(line_one)

            line_two = self.__next_line_raise_if_missing_instructions()
            instructions_list = self.__make_instructions_list(pos, direction, line_two)

            instructions = Instructions(instructions_list)
            yield instructions

            line_one = self.__next_line_raise_if_missing_instructions(next_instruction_expected=True)
