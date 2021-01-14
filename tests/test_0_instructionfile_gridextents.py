import unittest

import os
import glob
import shutil

from src.instructionfile import (
    InstructionsFile,
    ExceptionFileParseCritical
)
from src.location import Pos


class TestInstructionFileBase(unittest.TestCase):
    TEST_DIR_PREFIX = 'TestDir_RoboMars'

    def __remove_test_dirs(self):
        for directory in glob.glob(f'{TestInstructionFileBase.TEST_DIR_PREFIX}*'):
            if os.path.isdir(directory):
                try:
                    shutil.rmtree(directory)
                except FileNotFoundError:
                    pass

    def setUp(self):
        self.__remove_test_dirs()

    def tearDown(self):
        self.__remove_test_dirs()

    def _create_dir(self, dir_suffix=''):
        dir_name = f'{TestInstructionFileBase.TEST_DIR_PREFIX}{dir_suffix}'
        os.mkdir(dir_name)
        return dir_name


class TestInstructionFile_GridExtents(TestInstructionFileBase):

    def test_no_file(self):
        dir_name = self._create_dir('DOES_NOT_EXIST_test')
        filepath = f'{dir_name}/no_such_file'
        inst_file_processor = InstructionsFile(filepath)
        with self.assertRaises(ExceptionFileParseCritical) as exception_context:
            inst_file_processor.initialise_instructions()
        self.assertEqual(str(exception_context.exception), f'ERROR - File not found.')
        self.assertEqual(exception_context.exception.code, ExceptionFileParseCritical.CODE_NOT_FOUND)
        self.assertEqual(exception_context.exception.path, filepath)
        self.assertIsNone(exception_context.exception.line_num)

    def test_directory_specified_as_input(self):
        dir_name = self._create_dir('dirinput')
        filepath = f'{dir_name}'
        inst_file_processor = InstructionsFile(filepath)
        with self.assertRaises(ExceptionFileParseCritical) as exception_context:
            inst_file_processor.initialise_instructions()
        self.assertEqual(str(exception_context.exception), f'ERROR - Not a file.')
        self.assertEqual(exception_context.exception.code, ExceptionFileParseCritical.CODE_NOT_FILE)
        self.assertEqual(exception_context.exception.path, filepath)
        self.assertIsNone(exception_context.exception.line_num)

    def test_empty_file(self):
        dir_name = self._create_dir('emptyfile')
        filepath = f'{dir_name}/instfile'
        open(filepath, 'a').close()
        inst_file_processor = InstructionsFile(filepath)
        with self.assertRaises(ExceptionFileParseCritical) as exception_context:
            inst_file_processor.initialise_instructions()
        self.assertEqual(str(exception_context.exception), f'ERROR - Missing grid extents.')
        self.assertEqual(exception_context.exception.code, ExceptionFileParseCritical.CODE_MISSING_GRID_MAX)
        self.assertEqual(exception_context.exception.path, filepath)
        self.assertEqual(exception_context.exception.line_num, 0)
        # filepath = f'{filepath}_1'
        # with open(filepath, 'a') as fl:
        #     fl.write('')
        # inst_file_processor = InstructionsFile(filepath)
        # with self.assertRaises(ExceptionFileParseCritical) as exception_context:
        #     inst_file_processor.initialise_instructions()
        # self.assertEqual(str(exception_context.exception), f'ERROR - Missing grid extents.')
        # self.assertEqual(exception_context.exception.code, ExceptionFileParseCritical.CODE_MISSING_GRID_MAX)
        # self.assertEqual(exception_context.exception.path, filepath)
        # self.assertEqual(exception_context.exception.line_num, 0)

    def test_incorrect_first_line(self):
        dir_name = self._create_dir('bad_grid')
        filepath = f'{dir_name}/instfile'
        files = [
            (f'{filepath}_0', '''x'''),
            (f'{filepath}_1', '''1 1 E\nLRF'''),
            (f'{filepath}_2', ''' 1 1 E\nLRF''')
        ]
        for afile in files:
            with open(afile[0], 'a') as fl:
                fl.write(afile[1])
            inst_file_processor = InstructionsFile(afile[0])
            with self.assertRaises(ExceptionFileParseCritical) as exception_context:
                inst_file_processor.initialise_instructions()
            self.assertEqual(str(exception_context.exception), f'ERROR - Missing grid extents.')
            self.assertEqual(exception_context.exception.code, ExceptionFileParseCritical.CODE_MISSING_GRID_MAX)
            self.assertEqual(exception_context.exception.path, afile[0])
            self.assertEqual(exception_context.exception.line_num, 1)
            self.assertEqual(exception_context.exception.line, afile[1].splitlines()[0])

    def test_read_grid_extents(self):
        dir_name = self._create_dir('gridext')
        filepath = f'{dir_name}/instfile'
        files = [
            (f'{filepath}_0', '''5 3'''),
            (f'{filepath}_1', '''  5 3 \nxxxxxx'''),
            (f'{filepath}_2', ''' 5    3    \nyyyyy''')
        ]
        for afile in files:
            with open(afile[0], 'a') as fl:
                fl.write(afile[1])
            inst_file_processor = InstructionsFile(afile[0])
            inst_file_processor.initialise_instructions()
            grid_extents = inst_file_processor.grid_extents
            self.assertEqual(grid_extents.coord_x, 5)
            self.assertEqual(grid_extents.coord_y, 3)
