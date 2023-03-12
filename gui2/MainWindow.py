#!/usr/bin/env python
# coding: utf-8

import sys

import ttkbootstrap as ttk

from ..core.ProjConfig import Preference
from ..core.Utils import EDITION

class RplGenStudioMainWindow(ttk.Window):
    def __init__(
            self,preference:Preference = Preference()
            )->None:
        super().__init__(
            title       = '回声工坊' + EDITION,
            themename   = 'litera',
            iconphoto   = './media/icon.ico',
            # size,
            # position,
            # minsize,
            # maxsize,
            # resizable,
            # hdpi,
            # scaling,
            # transient,
            # overrideredirect,
            alpha=1)
        self.mainloop()