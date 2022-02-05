class Redirect:
    def __init__(self, file_path, print, console):
        self.log_file = open(file_path, "a+")
        self.print = print
        self.console = console

    def write(self, data):
        data = data.replace("\n\n", "\n")
        if self.print:
            print(data)
        if "Traceback" in data:
            self.log_file.write("\n---------------------------------------------\n")
            self.log_file.write(data)
            self.console.error_log("Ignored error. See ./data/logs/errors.log.")
        elif "Ignoring exception in" not in data:
            self.log_file.write(data)

        self.log_file.flush()
