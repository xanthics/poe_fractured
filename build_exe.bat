pyinstaller --clean -F -w --add-data favicon.ico;. --icon=appicon.ico -n fractured_watcher_x86-64.single_file.exe xangui.pyw
pyinstaller --clean -D -w --add-data favicon.ico;. --icon=appicon.ico -n fractured_watcher_x86-64.multi_file xangui.pyw
pause