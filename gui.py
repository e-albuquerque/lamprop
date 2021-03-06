# file: gui.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
# lamprop GUI - main program.
#
# Copyright © 2018,2020 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2018-01-21 17:55:29 +0100
# Last modified: 2020-12-30T11:46:36+0100
#
# SPDX-License-Identifier: BSD-2-Clause

from functools import partial
import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.font import nametofont
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
import lp


class LampropUI(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.directory = ""
        self.lamfile = tk.StringVar()
        self.lamfile.set("no file selected")
        self.laminates = None
        self.engprop = tk.IntVar()
        self.engprop.set(1)
        self.result = None
        self.matrices = tk.IntVar()
        self.fea = tk.IntVar()
        self.initialize()

    def initialize(self):
        """Create the GUI."""
        # Set the font
        default_font = nametofont("TkDefaultFont")
        default_font["size"] = 12
        self.option_add("*Font", default_font)
        # General commands and bindings
        self.rowconfigure(7, weight=1)
        self.columnconfigure(4, weight=1)
        # Create widgets.
        # Row
        prbut = ttk.Button(self, text="File:", command=self.do_fileopen)
        prbut.grid(row=0, column=0, sticky="w")
        fnlabel = ttk.Label(self, anchor="w", textvariable=self.lamfile)
        fnlabel.grid(row=0, column=1, columnspan=4, sticky="ew")
        # Row
        rldbut = ttk.Button(self, text="Reload", command=self.do_reload)
        rldbut.grid(row=1, column=0, sticky="w")
        # Row
        sal = ttk.Label(self, text="Save as:")
        sal.grid(row=2, column=0, sticky="w")
        txtbtn = ttk.Button(
            self, text="text", command=self.do_savetxt, state="disabled"
        )
        txtbtn.grid(row=2, column=1, sticky="w")
        self.txtbtn = txtbtn
        htmlbtn = ttk.Button(
            self, text="html", command=self.do_savehtml, state="disabled"
        )
        self.htmlbtn = htmlbtn
        htmlbtn.grid(row=2, column=2, sticky="w")
        # Row
        cb = partial(self.on_laminate, event=0)
        chkengprop = ttk.Checkbutton(
            self, text="Engineering properties", variable=self.engprop, command=cb
        )
        chkengprop.grid(row=3, column=0, columnspan=3, sticky="w")
        # Row
        chkmat = ttk.Checkbutton(
            self, text="ABD & H matrices, stiffness tensor", variable=self.matrices, command=cb
        )
        chkmat.grid(row=4, column=0, columnspan=3, sticky="w")
        # Row
        chkmat = ttk.Checkbutton(
            self, text="FEA material data", variable=self.fea, command=cb
        )
        chkmat.grid(row=5, column=0, columnspan=3, sticky="w")
        # Row
        cxlam = ttk.Combobox(self, state="readonly", justify="left")
        cxlam.grid(row=6, column=0, columnspan=5, sticky="we")
        cxlam.bind("<<ComboboxSelected>>", self.on_laminate)
        self.cxlam = cxlam
        # Row
        fixed = nametofont("TkFixedFont")
        fixed["size"] = 12
        res = ScrolledText(self, state="disabled", font=fixed)
        res.grid(row=7, column=0, columnspan=5, sticky="nsew")
        self.result = res

    # Callbacks
    def do_fileopen(self):
        if not self.directory:
            self.directory = ""
            available = [
                os.environ[k] for k in ("HOME", "HOMEDRIVE") if k in os.environ
            ]
            if available:
                self.directory = available[0]
        fn = filedialog.askopenfile(
            title="Lamprop file to open",
            parent=self,
            defaultextension=".lam",
            filetypes=(("lamprop files", "*.lam"), ("all files", "*.*")),
            initialdir=self.directory,
        )
        if not fn:
            return
        self.directory = os.path.dirname(fn.name)
        self.lamfile.set(fn.name)
        self.do_reload()
        self.txtbtn["state"] = "enabled"
        self.htmlbtn["state"] = "enabled"

    def do_reload(self):
        """Reload the laminates."""
        laminates = lp.parse(self.lamfile.get())
        if not laminates:
            return
        self.laminates = {lam.name: lam for lam in laminates}
        self.cxlam["values"] = list(self.laminates.keys())
        self.cxlam.current(0)
        self.on_laminate(0)

    def gentxt(self):
        name = self.cxlam.get()
        text = "\n".join(
            lp.text.out(
                self.laminates[name],
                bool(self.engprop.get()),
                bool(self.matrices.get()),
                bool(self.fea.get()),
            )
        )
        return text

    def on_laminate(self, event):
        """Laminate choice has changed."""
        text = self.gentxt()
        self.result["state"] = "normal"
        self.result.replace("1.0", "end", text)
        self.result["state"] = "disabled"

    def do_savetxt(self):
        res = filedialog.asksaveasfile(
            title="Save as text",
            parent=self,
            defaultextension=".txt",
            filetypes=(("text files", "*.txt"), ("all files", "*.*")),
            initialdir=self.directory,
            initialfile=self.cxlam.get() + ".txt",
        )
        if not res:
            return
        text = self.gentxt()
        with open(res.name, "w") as tf:
            tf.write(text)

    def do_savehtml(self):
        res = filedialog.asksaveasfile(
            title="Save as HTML",
            parent=self,
            defaultextension=".html",
            filetypes=(("HTML files", "*.html"), ("all files", "*.*")),
            initialdir=self.directory,
            initialfile=self.cxlam.get() + ".html",
        )
        if not res:
            return
        name = self.cxlam.get()
        html = "\n".join(
            lp.html.out(
                self.laminates[name],
                bool(self.engprop.get()),
                bool(self.matrices.get()),
                bool(self.fea.get()),
            )
        )
        with open(res.name, "w") as hf:
            hf.write(html)


def main():
    """Main entry point for lamprop GUI."""
    if os.name == "posix":
        if os.fork():
            sys.exit()
    else:
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(
            os.path.join(os.getenv("TEMP"), "stderr-" + os.path.basename(sys.argv[0])),
            "w",
        )
    root = LampropUI(None)
    root.wm_title("Lamprop GUI v" + lp.__version__)
    root.mainloop()


if __name__ == "__main__":
    main()
