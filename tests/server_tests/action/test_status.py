from __future__ import absolute_import, print_function, unicode_literals

import platform
import unittest

import conformity
import six

import pysoa
from pysoa.common.types import ActionResponse
from pysoa.server.action.status import (
    BaseStatusAction,
    StatusActionFactory,
)
from pysoa.server.types import EnrichedActionRequest


class _ComplexStatusAction(BaseStatusAction):
    _version = '7.8.9'

    _build = 'complex_service-28381-7.8.9-16_04'

    def check_good(self):
        self.diagnostics['check_good_called'] = True

    @staticmethod
    def check_warnings():
        return (
            (False, 'FIRST_CODE', 'First warning'),
            (False, 'SECOND_CODE', 'Second warning'),
        )

    @staticmethod
    def check_errors():
        return [
            [True, 'ANOTHER_CODE', 'This is an error'],
        ]


class TestBaseStatusAction(unittest.TestCase):
    def test_cannot_instantiate_base_action(self):
        with self.assertRaises(RuntimeError):
            BaseStatusAction()

    def test_build_implemented_version_not_implemented(self):
        class _Action(BaseStatusAction):
            pass

        action = _Action()
        self.assertIsNone(action._build)

        with self.assertRaises(NotImplementedError):
            print(action._version)

    def test_basic_status_works(self):
        action_request = EnrichedActionRequest(action='status', body={}, switches=None)

        response = StatusActionFactory('1.2.3', 'example_service-72-1.2.3-python3')()(action_request)

        self.assertIsInstance(response, ActionResponse)
        self.assertEqual(
            {
                'build': 'example_service-72-1.2.3-python3',
                'conformity': six.text_type(conformity.__version__),
                'healthcheck': {'diagnostics': {}, 'errors': [], 'warnings': []},
                'pysoa': six.text_type(pysoa.__version__),
                'python': six.text_type(platform.python_version()),
                'version': '1.2.3',
            },
            response.body,
        )

    def test_complex_status_works(self):
        action_request = EnrichedActionRequest(action='status', body={}, switches=None)

        response = _ComplexStatusAction()(action_request)

        self.assertIsInstance(response, ActionResponse)
        self.assertEqual(
            {
                'build': 'complex_service-28381-7.8.9-16_04',
                'conformity': six.text_type(conformity.__version__),
                'healthcheck': {
                    'diagnostics': {'check_good_called': True},
                    'errors': [('ANOTHER_CODE', 'This is an error')],
                    'warnings': [('FIRST_CODE', 'First warning'), ('SECOND_CODE', 'Second warning')],
                },
                'pysoa': six.text_type(pysoa.__version__),
                'python': six.text_type(platform.python_version()),
                'version': '7.8.9',
            },
            response.body,
        )
