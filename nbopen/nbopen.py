#!/usr/bin/python3
import argparse
import os.path
import webbrowser
from notebook import notebookapp
from notebook.utils import url_path_join, url_escape
import nbformat
import subprocess
import time
import timeout_decorator
from traitlets.config.configurable import Configurable
from traitlets import Int
import platform
import tempfile
import subprocess
import os
from pathlib import Path
import time

from .traitlets import ModeString


class Opener(Configurable):
    mode = ModeString(config=True)
    timeout = Int(config=True)


opener = Opener()


def find_best_server(filename: str) -> int:
    servers = [si for si in notebookapp.list_running_servers()
               if filename.startswith(si['notebook_dir'])]
    try:
        return max(servers, key=lambda si: len(si['notebook_dir']))
    except ValueError:
        return None


@timeout_decorator.timeout(opener.timeout, use_signals=False)
def wait_best_server(filename: str, server_inf):
    while server_inf is None:
        time.sleep(0.1)
        server_inf = find_best_server(filename)
    return server_inf


def nbopen(filename: str):
    filename = os.path.abspath(filename)
    home_dir = os.path.expanduser('~')
    server_inf = find_best_server(filename)
    if server_inf is None:
        if filename.startswith(home_dir):
            nbdir = home_dir
        else:
            nbdir = os.path.dirname(filename)

        print("Starting new server at", nbdir)
        # to get server with find_best_server,
        # launch app by jupyter-notebook
        # even if you use JupyterLab
        pf = platform.system()
        if pf == 'Windows':
            with tempfile.NamedTemporaryFile("w", suffix=".vbs", delete=False) as fp:
                fp.write('Set ws = CreateObject("Wscript.Shell")\n'
                         f'ws.run "cmd /c jupyter-notebook.bat {nbdir} --no-browser", vbhide')
                subprocess.Popen(["cscript.exe", fp.name], shell=True)
            server_inf = wait_best_server(filename, server_inf)
            os.unlink(fp.name)
        else:
            subprocess.Popen(["jupyter-notebook", "--no-browser", nbdir],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, shell=True)
            server_inf = wait_best_server(filename, server_inf)

    print("Using existing server at", server_inf['notebook_dir'])
    path = os.path.relpath(filename, start=server_inf['notebook_dir'])
    if os.sep != '/':
        path = path.replace(os.sep, '/')
    if opener.mode == "notebook":
        url = url_path_join(server_inf['url'], 'notebooks', url_escape(path))
    elif opener.mode == "lab":
        url = url_path_join(server_inf['url'], 'lab/tree', url_escape(path))
    browser = webbrowser.get(None)
    browser.open(url, new=0)


def nbnew(filename: str) -> str:
    if not filename.endswith('.ipynb'):
        filename += '.ipynb'
    if os.path.exists(filename):
        msg = "Notebook {} already exists"
        print(msg.format(filename))
        print("Opening existing notebook")
    else:
        nb_version = nbformat.versions[nbformat.current_nbformat]
        nbformat.write(nb_version.new_notebook(),
                       filename)
    return filename


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('-n', '--new', action='store_true', default=False,
                    help='Create a new notebook file with the given name.')
    ap.add_argument('filename', help='The notebook file to open')

    args = ap.parse_args(argv)
    if args.new:
        filename = nbnew(args.filename)
    else:
        filename = args.filename

    nbopen(filename)


if __name__ == '__main__':
    main()
