def show():
  print '''Usage: envtransfer COMMAND [ARGS]

  EnvTransfer command line tool.

Commands:
  auth       Authorization. Get token
  upload     Upload your environment
  download   Download your environment
  help       Show this message and exit
'''

__name__ == '__main__' and show()
