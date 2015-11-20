from smartva.symptom_prep import SymptomPrep


class TestSymptomPrep(object):
    def test_copy_variables(self):
        headers = ['test1', 'test2', 'test3', 'test4']
        row = dict(zip(headers, [2, 37, 0, 0]))

        conversion_map = {
            'test1': 'test3',
            'test2': 'test4',
        }

        SymptomPrep.copy_variables(row, conversion_map)

        assert row == dict(zip(headers, [2, 37, 2, 37]))

    def test_process_progressive_data(self):
        headers = ['test0', 'test1', 'test2', 'test3', 'test4']
        rows = [
            dict(zip(headers, [72, 0, 0, 0, 0])),
            dict(zip(headers, [12, 0, 0, 0, 0])),
            dict(zip(headers, [35, 0, 0, 0, 0])),
            dict(zip(headers, [48, 0, 0, 0, 0])),
        ]

        valid_results = [
            dict(zip(headers, [72, 0, 0, 0, 1])),
            dict(zip(headers, [12, 1, 0, 0, 0])),
            dict(zip(headers, [35, 0, 1, 0, 0])),
            dict(zip(headers, [48, 0, 0, 1, 0])),
        ]

        conversion_map = {
            'test0': [
                (65, 'test4'),
                (45, 'test3'),
                (25, 'test2'),
                (0, 'test1')
            ]
        }

        for i, row in enumerate(rows):
            SymptomPrep.process_progressive_value_data(row, conversion_map.items())

            assert row == valid_results[i]

    def test_process_cutoff_data(self):
        headers = ['test1', 'test2', 'test3', 'test4']
        row = dict(zip(headers, [0.12345, 40, 20, '']))

        conversion_map = {
            'test1': 0.1234,
            'test2': 50,
            'test3': 10,
            'test4': 1
        }

        SymptomPrep.process_cutoff_data(row, conversion_map.items())

        assert row == dict(zip(headers, [1, 0, 1, 0]))

    def test_process_injury_data(self):
        headers = ['test0', 'test1', 'test2', 'test3', 'test4']
        rows = [
            dict(zip(headers, [999, 1, 0, 1, 0])),
            dict(zip(headers, [40, 1, 0, 1, 0])),
            dict(zip(headers, [28, 1, 0, 1, 0])),
        ]

        valid_results = [
            dict(zip(headers, [999, 0, 0, 0, 0])),
            dict(zip(headers, [40, 0, 0, 0, 0])),
            dict(zip(headers, [28, 1, 0, 1, 0])),
        ]

        conversion_map = {
            ('test0', 30): ['test1', 'test2', 'test3', 'test4']
        }

        for i, row in enumerate(rows):
            SymptomPrep.process_injury_data(row, conversion_map.items())

            assert row == valid_results[i]

    def test_post_process_binary_variables(self):
        headers = ['test1', 'test2', 'test3', 'test4']
        row = dict(zip(headers, [1, 2, 0, '']))

        conversion_map = ['test1', 'test2', 'test3', 'test4']

        SymptomPrep.post_process_binary_variables(row, conversion_map)

        assert row == dict(zip(headers, [1, 0, 0, 0]))