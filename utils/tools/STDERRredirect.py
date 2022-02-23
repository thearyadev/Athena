from ..tools.console import Console


class Redirect:
    """
    Redirects stderr to the error file to avoid cluttering the console for errors that were not caught by Nextcord
    """

    def __init__(self, file_path: str, print: bool, console: Console):
        self.log_file = open(file_path, "a+")  # log file in append mode.
        self.print = print
        self.console = console

    def write(self, data):
        data = data.replace("\n\n", "\n")
        if self.print:  # if print is true, dump the errors into console.
            print(data)
        if "Traceback" in data: # parse the traceback. Otherwise, it looks weird in the text file.
            self.log_file.write("\n---------------------------------------------\n") # to split tracebacks
            self.log_file.write(data)
            self.console.error_log("Ignored error. See ./data/logs/errors.log.")
        elif "Ignoring exception in" not in data:
            self.log_file.write(data)

        self.log_file.flush()
