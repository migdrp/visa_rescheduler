class Logger:

  enviroment:str =  'local'

  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  reset = '\033[0m '
  bright = '\033[1m'
  underline = '\033[4m'
  black = '\033[30m'
  red = '\033[38;2;255;57;43m'
  green = '\033[38;2;154;255;0m'
  yellow = '\033[38;2;255;238;0m'
  blue = '\033[34m'
  magenta = '\033[35m'
  cyan = '\033[36m'
  white = '\033[37m'

  def __init__(self, name:str) -> None:
    self.name = name

  def debug(self, message:str, variable=''):
    if (self.enviroment == 'local'):
      print(f'\n{self.bright}{self.cyan}[{self.name}] {self.green}{message}{self.reset}', variable)
    if (self.enviroment == 'dev'):
      print(f'\n[{self.name}] {message}:', variable)
    if (self.enviroment == 'prod'):
      return

  def info(self, message:str, variable=''):
    if (self.enviroment == 'local'):
      print(f'\n{self.bright}{self.yellow}[{self.name}] {self.green}{message}{self.reset}', variable)
    if (self.enviroment == 'dev'):
      print(f'\n[{self.name}] {message}:', variable)
    if (self.enviroment == 'prod'):
      return

  def error(self, message:str, variable=''):
    if (self.enviroment == 'local'):
      print(f'\n{self.bright}{self.yellow}[{self.name}] {self.red}{message}{self.reset}', variable)
    if (self.enviroment == 'dev'):
      print(f'\n[{self.name}] {message}:', variable)
    if (self.enviroment == 'prod'):
      return
