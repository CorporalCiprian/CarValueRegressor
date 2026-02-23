#!/usr/bin/env python3
import multiprocessing

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)

from nicegui import ui
from ui.tabs.train import train_tab
from ui.tabs.predict import predict_tab


@ui.page('/')
def main_page():
    ui.dark_mode().enable()
    ui.colors(primary='#6366f1')

    with ui.header().classes('bg-gray-900 items-center justify-between px-6 py-3 shadow-lg'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('directions_car', size='sm').classes('text-indigo-400')
            ui.label('Car Value Regressor').classes('text-xl font-bold text-white')

    with ui.column().classes('w-full max-w-2xl mx-auto p-6 gap-0'):
        with ui.card().classes('w-full bg-gray-900 rounded-2xl shadow-xl overflow-hidden p-0'):
            with ui.tabs().classes('w-full bg-gray-800') as tabs:
                t1 = ui.tab('Train', icon='model_training')
                t2 = ui.tab('Predict', icon='directions_car')

            with ui.tab_panels(tabs, value=t1).classes('w-full bg-gray-900'):
                with ui.tab_panel(t1):
                    train_tab()
                with ui.tab_panel(t2):
                    predict_tab()


if __name__ in {'__main__', '__mp_main__'}:
    multiprocessing.freeze_support()
    ui.run(native=True, window_size=(700, 650), title='Car Value Regressor')