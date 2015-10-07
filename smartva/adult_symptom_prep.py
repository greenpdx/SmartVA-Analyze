import csv
import os

from smartva.data_prep import DataPrep
from smartva.loggers import status_logger
from smartva.utils import status_notifier, get_item_count
from smartva.adult_symptom_data import (
    GENERATED_HEADERS,
    ADULT_CONVERSION_VARIABLES,
    COPY_VARIABLES,
    AGE_QUARTILE_BINARY_VARIABLES,
    DURATION_CUTOFF_DATA,
    INJURY_VARIABLES,
    BINARY_VARIABLES,
    FREE_TEXT_VARIABLES,
    DROP_LIST,
    BINARY_CONVERSION_MAP
)
from smartva.utils.conversion_utils import additional_headers_and_values

FILENAME_TEMPLATE = '{:s}-symptom.csv'


class AdultSymptomPrep(DataPrep):
    AGE_GROUP = 'adult'

    def run(self):
        status_logger.info('Adult :: Processing Adult symptom data')
        status_notifier.update({'progress': (3,)})

        with open(os.path.join(self.output_dir, FILENAME_TEMPLATE.format(self.AGE_GROUP)), 'wb') as fo:
            writer = csv.writer(fo)

            with open(self.input_file_path, 'rb') as fi:
                reader = csv.reader(fi)
                records = get_item_count(reader, fi) - 1
                status_notifier.update({'sub_progress': (0, records)})

                headers = next(reader)

                additional_headers_data = GENERATED_HEADERS
                additional_headers, additional_values = additional_headers_and_values(headers, additional_headers_data)

                headers.extend(additional_headers)

                self.rename_headers(headers, ADULT_CONVERSION_VARIABLES)

                not_drop_list = ADULT_CONVERSION_VARIABLES.values() + FREE_TEXT_VARIABLES + additional_headers

                drop_index_list = set([i for i, header in enumerate(headers) if header not in not_drop_list])
                drop_index_list.update([headers.index(header) for header in DROP_LIST])

                writer.writerow(self.drop_from_list(headers, drop_index_list))

                for index, row in enumerate(reader):
                    if self.want_abort:
                        return False

                    status_notifier.update({'sub_progress': (index,)})

                    new_row = row + additional_values

                    for read_header, write_header in COPY_VARIABLES.items():
                        new_row[headers.index(write_header)] = new_row[headers.index(read_header)]

                    # Compute age quartiles.
                    for read_header, conversion_data in AGE_QUARTILE_BINARY_VARIABLES.items():
                        for value, write_header in conversion_data:
                            if int(new_row[headers.index(read_header)]) > value:
                                new_row[headers.index(write_header)] = 1
                                break


                    for header, cutoff_data in DURATION_CUTOFF_DATA.items():
                        try:
                            new_row[headers.index(header)] = int(float(new_row[headers.index(header)]) >= cutoff_data)
                        except ValueError:
                            new_row[headers.index(header)] = 0

                    # The "var list" variables in the loop below are all indicators for different questions about
                    # injuries (road traffic, fall, fires) We only want to give a VA a "1"/yes response for that
                    # question if the injury occurred within 30 days of death (i.e. s163<=30) Otherwise, we could
                    # have people who responded that they were in a car accident 20 years prior to death be assigned
                    # to road traffic deaths

                    for header, injury_list in INJURY_VARIABLES.items():
                        if float(new_row[headers.index(header)]) > 30:
                            for injury in injury_list:
                                new_row[headers.index(injury)] = 0

                    # dichotomize!
                    self.convert_binary_variables(headers, new_row, BINARY_CONVERSION_MAP.items())

                    # ensure all binary variables actually ARE 0 or 1:
                    for header in BINARY_VARIABLES:
                        try:
                            value = int(new_row[headers.index(header)])
                        except ValueError:
                            value = 0
                        new_row[headers.index(header)] = int(value == 1)

                    writer.writerow(self.drop_from_list(new_row, drop_index_list))

        status_notifier.update({'sub_progress': None})

        return True

    def abort(self):
        self.want_abort = True
