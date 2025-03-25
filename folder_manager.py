import datetime
import os
import pandas as pd


class Folder:
    def __init__(self):
        self.discharge = False
        self.exp_n = 0

        self.base_folder = "/CMFX_RAW/"

        self.video_folder = f"{self.base_folder}video/CMFX_{0:05d}/"
        self.spectrometer_folder = f"{self.base_folder}spectrometer/"
        self.interferometer_folder = f"{self.base_folder}interferometer/"
        self.image_folder = f"{self.base_folder}image/"
        self.logs_folder = "/CMFX_RAW/logs/2024_04_23"  # this is the first day with logs
        # self.create_folders()

    def create_folders(self, dsc=0, n=0):
        print(f"creating folders dsc={dsc}, n={n}")
        if dsc == 1:
            self.base_folder = "/CMFX_RAW/"
            now_str = ''
        else:
            print("IT IS A TEST RUN")
            self.base_folder = "/CMFX_RAW/tests/"

            if n == 0:
                now_str = f"_{datetime.datetime.now().strftime('%y%m%d_%H%M%S')}"
            else:
                now_str = ''
        # today_str = f"_{datetime.datetime.now().strftime('%y%m%d_%H%M%S')}"
        self.video_folder = f"{self.base_folder}video/CMFX_{n:05d}/"
        check_create_folder(self.video_folder)
        self.spectrometer_folder = f"{self.base_folder}spectrometer/"
        check_create_folder(self.spectrometer_folder)
        self.interferometer_folder= f"{self.base_folder}interferometer/"
        check_create_folder(self.interferometer_folder)
        self.image_folder = f"{self.base_folder}image/img/"
        check_create_folder(self.image_folder)

        now = datetime.datetime.now()
        run_date = now.date().strftime('%Y_%m_%d')
        self.logs_folder = f"/CMFX_RAW/logs/{run_date}"
        check_create_folder(self.logs_folder)

        return True

    def update_folders(self, dsc=0, n=0):
        self.create_folders(dsc, n)
        return True


def check_create_folder(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"Folder '{path}' created.")
        except OSError as e:
            print(f"Failed to create folder '{path}': {e}")
    # else:
        # print(f"Folder '{path}' already exists.")


def save_results_to_parquet(results_columns, filename):
    if os.path.exists(filename):
        # Append a suffix to the filename if it already exists
        base_filename, ext = os.path.splitext(filename)
        suffix = 1
        while os.path.exists(f"{base_filename}_{suffix}{ext}"):
            suffix += 1
        filename = f"{base_filename}_{suffix}{ext}"

    # # Convert data to a DataFrame (you can customize this based on your data)
    # # df = pd.DataFrame(data)
    # results_df = pd.concat([pd.Series(val) for val in results], axis=1)
    # results_df.columns = [scope_columns[variable]['name'] for variable in scope_columns if
    #                       hasattr(scope, variable)]

    # Save DataFrame to Parquet file
    results_columns.to_parquet(filename, index=False)
    print(f"File: {filename} was written at {datetime.datetime.now().strftime('%y%m%d_%H%M%S')}")
