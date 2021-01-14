import unittest

import os
import glob
import shutil

from tests.test_0_instructionfile_gridextents import TestInstructionFileBase

from src.instructionfile import (
    InstructionsFile,
    ExceptionFileParseCritical
)
from src.location import Pos
from src.grid import Grid
from src.robot import Robot


class TestInstructionFile_Instructions(TestInstructionFileBase):

    def test_read_instructions_none_exist(self):
        dir_name = self._create_dir()
        filepath = f'{dir_name}/instfile'
        files = [
            (f'{filepath}_0', '''5 3'''),
            (f'{filepath}_1', '''5 3\n'''),
            (f'{filepath}_2', '''  5 3\n\n'''),
            (f'{filepath}_3', '''  5 3\n\n\n''')
        ]
        for afile in files:
            with open(afile[0], 'a') as fl:
                fl.write(afile[1])
            inst_file_processor = InstructionsFile(afile[0])
            inst_file_processor.initialise_instructions()
            grid_extents = inst_file_processor.grid_extents
            self.assertEqual(grid_extents.coord_x, 5)
            self.assertEqual(grid_extents.coord_y, 3)
            count = 0
            with self.assertRaises(ExceptionFileParseCritical) as exception_context:
                for robot_instruction in inst_file_processor.next_instructions():
                    count += 1
            self.assertEqual(count, 0)
            self.assertEqual(str(exception_context.exception), f'ERROR - robot instructions missing.')
            self.assertEqual(exception_context.exception.code, ExceptionFileParseCritical.CODE_ROBOT_INSTRUCTIONS_MISSING)
            self.assertEqual(exception_context.exception.path, afile[0])
            line_num_expected = afile[1].count('\n') or 1  # Lowest possible line number is 1
            self.assertEqual(exception_context.exception.line_num, line_num_expected)
            self.assertEqual(exception_context.exception.line, '')

    def test_read_instructions_bad_starting_state(self):
        dir_name = self._create_dir()
        filepath = f'{dir_name}/instfile'
        files = [
            (f'{filepath}_0', '''5 3\nLRF'''),
            (f'{filepath}_1', '''5 3\n\n\n l f'''),
            (f'{filepath}_2', '''5 3\nxyZ\n'''),
            (f'{filepath}_3', '''5 3\n 1 2\n'''),
            (f'{filepath}_4', '''5 3\n 1 2 n \n'''),
            (f'{filepath}_5', '''5 3\n\n 1 2 e \n''')
        ]
        for afile in files:
            with open(afile[0], 'a') as fl:
                fl.write(afile[1])
            inst_file_processor = InstructionsFile(afile[0])
            inst_file_processor.initialise_instructions()
            grid_extents = inst_file_processor.grid_extents
            self.assertEqual(grid_extents.coord_x, 5)
            self.assertEqual(grid_extents.coord_y, 3)
            count = 0
            with self.assertRaises(ExceptionFileParseCritical) as exception_context:
                for robot_instruction in inst_file_processor.next_instructions():
                    count += 1
            self.assertEqual(count, 0)
            self.assertEqual(str(exception_context.exception), f'ERROR - robot position and direction not recognised.')
            self.assertEqual(exception_context.exception.code, ExceptionFileParseCritical.CODE_ROBOT_POSITION_AND_DIRECTION_NOT_RECOGNISED)
            self.assertEqual(exception_context.exception.path, afile[0])
            self.assertGreater(exception_context.exception.line_num, 1)
            self.assertNotEqual(exception_context.exception.line, '')
            self.assertNotEqual(exception_context.exception.line, '5 3')

    def test_read_instructions_missing_instructions(self):
        dir_name = self._create_dir()
        filepath = f'{dir_name}/instfile'
        files = [
            (f'{filepath}_0', '''5 3\n1 1 E'''),
            (f'{filepath}_1', '''5 3\n\n\n   1 1 E'''),
            (f'{filepath}_2', '''5 3\n1 1 E\n''')
        ]
        for afile in files:
            with open(afile[0], 'a') as fl:
                fl.write(afile[1])
            inst_file_processor = InstructionsFile(afile[0])
            inst_file_processor.initialise_instructions()
            grid_extents = inst_file_processor.grid_extents
            self.assertEqual(grid_extents.coord_x, 5)
            self.assertEqual(grid_extents.coord_y, 3)
            count = 0
            with self.assertRaises(ExceptionFileParseCritical) as exception_context:
                for robot_instruction in inst_file_processor.next_instructions():
                    count += 1
            self.assertEqual(count, 0)
            self.assertEqual(str(exception_context.exception), f'ERROR - robot instructions missing.')
            self.assertEqual(exception_context.exception.code, ExceptionFileParseCritical.CODE_ROBOT_INSTRUCTIONS_MISSING)
            self.assertEqual(exception_context.exception.path, afile[0])
            self.assertGreater(exception_context.exception.line_num, 1)
            self.assertEqual(exception_context.exception.line, '')
            self.assertNotEqual(exception_context.exception.line, '5 3')

    def test_read_instructions_missing_instructions_of_next_robot(self):
        dir_name = self._create_dir()
        filepath = f'{dir_name}/instfile'
        files = [
            (f'{filepath}_0', '''5 3\n\n\n   1 1 E\nRFRFRFRF\n3 2 N'''),
            (f'{filepath}_1', '''5 3\n\n1 1 E\nRFRFRFRF\n\n3 2 N\n\n''')
        ]
        for afile in files:
            with open(afile[0], 'a') as fl:
                fl.write(afile[1])
            inst_file_processor = InstructionsFile(afile[0])
            inst_file_processor.initialise_instructions()
            grid_extents = inst_file_processor.grid_extents
            self.assertEqual(grid_extents.coord_x, 5)
            self.assertEqual(grid_extents.coord_y, 3)
            count = 0
            with self.assertRaises(ExceptionFileParseCritical) as exception_context:
                for robot_instruction in inst_file_processor.next_instructions():
                    count += 1
            self.assertEqual(count, 1)  # Every example above, has one good complete instruction
            self.assertEqual(str(exception_context.exception), f'ERROR - robot instructions missing.')
            self.assertEqual(exception_context.exception.code, ExceptionFileParseCritical.CODE_ROBOT_INSTRUCTIONS_MISSING)
            self.assertEqual(exception_context.exception.path, afile[0])
            self.assertGreater(exception_context.exception.line_num, 1)
            self.assertEqual(exception_context.exception.line, '')
            self.assertNotEqual(exception_context.exception.line, '5 3')

    def test_read_instructions_bad_instructions(self):
        dir_name = self._create_dir()
        filepath = f'{dir_name}/instfile'
        files = [
            (f'{filepath}_0', '''5 3\n1 1 E\nRFRFRYRF\n''', 'Character "Y" at position 5'),
            (f'{filepath}_1', '''5 3\n 1 1 E\n5 3''', 'Character "5" at position 0'),
            (f'{filepath}_2', '''5 3\n1 1 E\nLRFB\n''', 'Character "B" at position 3')
        ]
        for afile in files:
            with open(afile[0], 'a') as fl:
                fl.write(afile[1])
            inst_file_processor = InstructionsFile(afile[0])
            inst_file_processor.initialise_instructions()
            grid_extents = inst_file_processor.grid_extents
            self.assertEqual(grid_extents.coord_x, 5)
            self.assertEqual(grid_extents.coord_y, 3)
            count = 0
            with self.assertRaises(ExceptionFileParseCritical) as exception_context:
                for robot_instruction in inst_file_processor.next_instructions():
                    count += 1
            self.assertEqual(count, 0)
            self.assertEqual(str(exception_context.exception), f'ERROR - robot instructions not recognised.')
            self.assertEqual(exception_context.exception.code, ExceptionFileParseCritical.CODE_ROBOT_INSTRUCTIONS_NOT_RECOGNISED)
            self.assertEqual(exception_context.exception.path, afile[0])
            self.assertEqual(exception_context.exception.line_num, 3)
            self.assertEqual(exception_context.exception.line, afile[2])

    def test_read_instructions_one_robot_noloss(self):
        dir_name = self._create_dir()
        filepath = f'{dir_name}/allgood'
        afile = (f'{filepath}_0', '''5 3\n1 1 E\nRFRFRFRF\n''')
        with open(afile[0], 'a') as fl:
            fl.write(afile[1])
        inst_file_processor = InstructionsFile(afile[0])
        inst_file_processor.initialise_instructions()
        grid_extents = inst_file_processor.grid_extents
        self.assertEqual(grid_extents.coord_x, 5)
        self.assertEqual(grid_extents.coord_y, 3)
        grid = Grid(grid_extents)
        count = 0
        for robot_instruction in inst_file_processor.next_instructions():
            self.assertEqual(str(robot_instruction), '::Start[1,1,E] ::TurnRight ::MoveForward ::TurnRight ::MoveForward ::TurnRight ::MoveForward ::TurnRight ::MoveForward')
            robot = Robot()
            for inst in robot_instruction.instruction_list:
                inst.do(grid, robot)
            self.assertEqual(str(robot), '1 1 E')
            count += 1
        self.assertEqual(count, 1)

    def test_read_instructions_one_robot_getslost(self):
        dir_name = self._create_dir()
        filepath = f'{dir_name}/allgood'
        afile = (f'{filepath}_1', '''5 3\n3 2 N\nFRRFLLFFRRFLL\n''')
        with open(afile[0], 'a') as fl:
            fl.write(afile[1])
        inst_file_processor = InstructionsFile(afile[0])
        inst_file_processor.initialise_instructions()
        grid_extents = inst_file_processor.grid_extents
        self.assertEqual(grid_extents.coord_x, 5)
        self.assertEqual(grid_extents.coord_y, 3)
        grid = Grid(grid_extents)
        count = 0
        for robot_instruction in inst_file_processor.next_instructions():
            self.assertEqual(len(robot_instruction.instruction_list), 14)  # 14 instructions (13 moves + 1 start instruction).
            self.assertEqual(
                str(robot_instruction),
                '::Start[3,2,N] ::MoveForward ::TurnRight ::TurnRight ::MoveForward ::TurnLeft ::TurnLeft ::MoveForward ::MoveForward ::TurnRight ::TurnRight ::MoveForward ::TurnLeft ::TurnLeft'
            )
            robot = Robot()
            for inst in robot_instruction.instruction_list[:8]:  # First 8 instructions are good.
                inst.do(grid, robot)
            robot_instruction.instruction_list[8].do(grid, robot)  # Next instruction leads to robot being lost.
            self.assertEqual(str(robot), '3 3 N LOST')
            robot_instruction.instruction_list[9].do(grid, robot)
            robot_instruction.instruction_list[10].do(grid, robot)
            with self.assertRaises(Exception) as exception_context:
                robot_instruction.instruction_list[11].do(grid, robot)
            for inst in robot_instruction.instruction_list[12:]:
                inst.do(grid, robot)
            count += 1
        self.assertEqual(count, 1)

    def test_read_instructions_three_robots_oneloss_oneavoidance(self):
        dir_name = self._create_dir()
        filepath = f'{dir_name}/allgood'
        afile = (f'{filepath}_2', '''5 3\n\n1 1 E\nRFRFRFRF\n\n3 2 N\nFRRFLLFFRRFLL\n\n0 3 W\nLLFFFLFLFL\n''')
        expectations = (
            ('::Start[1,1,E] ::TurnRight ::MoveForward ::TurnRight ::MoveForward ::TurnRight ::MoveForward ::TurnRight ::MoveForward',
             '1 1 E'
             ),
            ('::Start[3,2,N] ::MoveForward ::TurnRight ::TurnRight ::MoveForward ::TurnLeft ::TurnLeft ::MoveForward ::MoveForward ::TurnRight ::TurnRight ::MoveForward ::TurnLeft ::TurnLeft',
             '3 3 N LOST'
             ),
            ('::Start[0,3,W] ::TurnLeft ::TurnLeft ::MoveForward ::MoveForward ::MoveForward ::TurnLeft ::MoveForward ::TurnLeft ::MoveForward ::TurnLeft',
             '2 3 S'
             ),
        )
        with open(afile[0], 'a') as fl:
            fl.write(afile[1])
        inst_file_processor = InstructionsFile(afile[0])
        inst_file_processor.initialise_instructions()
        grid_extents = inst_file_processor.grid_extents
        self.assertEqual(grid_extents.coord_x, 5)
        self.assertEqual(grid_extents.coord_y, 3)
        grid = Grid(grid_extents)
        count = 0
        for robot_instruction in inst_file_processor.next_instructions():
            self.assertEqual(str(robot_instruction), expectations[count][0])
            robot = Robot()
            for inst in robot_instruction.instruction_list:
                inst.do(grid, robot)
                if robot.is_lost:
                    break
            self.assertEqual(str(robot), expectations[count][1])
            count += 1
        self.assertEqual(count, 3)
