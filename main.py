#!/usr/bin/env python3
import multiprocessing

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)

from ui.tabs.maintab import run_app

if __name__ in {'__main__', '__mp_main__'}:
    multiprocessing.freeze_support()
    run_app()