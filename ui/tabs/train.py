from nicegui import ui


def train_tab():
    with ui.column().classes('w-full gap-4 p-4'):
        ui.label('Train the model').classes('text-2xl font-bold text-white')
        ui.separator()

        with ui.card().classes('w-full bg-gray-800 rounded-xl p-4 gap-2'):
            ui.label('Upload a JSON dataset to train the model.').classes('text-gray-400')
            ui.label('The file should contain a list of car records with features and a price field.') \
                .classes('text-gray-500 text-sm')

        ui.upload(on_upload=handle_upload, label='Drop JSON file here') \
            .props('accept=.json outlined') \
            .classes('w-full')

        ui.label('No model trained yet.') \
            .classes('text-gray-500 text-sm text-center') \
            .mark('train-status')


def handle_upload(e):
    import json
    data = json.loads(e.content.read())
    ui.notify('Training started...', type='positive', icon='check')