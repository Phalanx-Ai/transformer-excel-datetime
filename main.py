import logging
import csv

from kbc.env_handler import KBCEnvHandler
from pathlib import Path
from datetime import datetime

APP_VERSION = "0.1.0"

class Component(KBCEnvHandler):
    MANDATORY_PARS = [
        "datetime_columns"
    ]

    def __init__(self):
        # for easier local project setup
        default_data_dir = Path(__file__).resolve().parent.joinpath('data').as_posix() \
            if not os.environ.get('KBC_DATADIR') else None

        KBCEnvHandler.__init__(
            self,
            self.MANDATORY_PARS,
            log_level=logging.INFO,
            data_path=default_data_dir
        )

        logging.info('Running version %s', APP_VERSION)
        logging.info('Loading configuration...')

        try:
            self.validate_config(self.MANDATORY_PARS)

        except ValueError as e:
            logging.exception(e)
            exit(1)

    def run(self):
        def _floatHourToTime(fh):
            """ From: https://stackoverflow.com/questions/31359150/convert-date-from-excel-in-number-format-to-date-format-python """
            h, r = divmod(fh, 1)
            m, r = divmod(r*60, 1)
            return (int(h), int(m), int(r*60))

        columns_to_transform = self.cfg_params['datetime_columns'].split(',')

        ## NEW CODE::
        for input_table in self.get_input_tables_definitions():
            with open(input_table.full_path, 'r') as input_file:
                output_filename = '%s/%s' % (self.tables_out_path, input_table.file_name)

                lazy_lines = (line.replace('\0', '') for line in input_file)

                reader = csv.DictReader(lazy_lines, lineterminator='\n')
                writer = csv.DictWriter(output_filename, fieldnames=reader.fieldnames, lineterminator='\n')
                writer.writeheader()

                for row in reader:
                    for col in columns_to_transform:
                        dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(float(row[col])) - 2)
                        hour, minute, second = _floatHourToTime(float(row[col]) % 1)
                        dt = dt.replace(hour=hour, minute=minute, second=second)
                        row[c] = int(dt.timestamp())

                    writer.writerow(row)
