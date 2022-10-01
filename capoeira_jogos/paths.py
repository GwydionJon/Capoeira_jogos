import pathlib
import os


def make_app_link():
    print("test")
    main_py_path = pathlib.Path(__file__).parent.absolute() / "main.py"
    desktop = pathlib.Path(os.path.expanduser("~/Desktop")) / "jogosApp.py"
    if not os.path.exists(desktop):
        desktop.symlink_to(main_py_path)
    else:
        print("Symlink already exists")
