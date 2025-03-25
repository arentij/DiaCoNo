import logging


def setup_logger(name, log_file, level=logging.INFO):
    # """To set up as many loggers as you want"""
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    # if name == 'control_log':
    #     try:
    #         os.chmod(log_file, 0o777)
    #     except PermissionError:
    #         print('File already was created by someone else')
    return logger


#
# if __name__ == "__main__":
#     # print(1)
#     today = str(datetime.date.today())
#     today = today[5:7] + today[8:10] + today[2:4]
#     file_name_logger = '/data/3m/' + str(today) + '/control.log'
#
#     control_logger = setup_logger('control_log', file_name_logger)
#
#     while True:
#         now = datetime.datetime.now()
#         ssm = str((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
#         time.sleep(3)
#         control_logger.info(ssm + '\t' + str(1))