from pathlib import Path
from nicegui import ui, run
from regressor.trainer import train as train_model

DATA_DIR = Path(__file__).parent.parent.parent / 'data'
MODEL_PATH = DATA_DIR / 'regressor.pkl'

JSON_TEMPLATE = [
    {
        "price": "12500",
        "source": "autovit",
        "attributes": {
            "Marca": "Volkswagen",
            "Model": "Golf",
            "Anul productiei": "2018",
            "Rulaj": "85000 km",
            "Putere": "115 CP",
            "Combustibil": "Benzina",
            "Cutie de viteze": "Manuala",
            "Numar de portiere": "5"
        }
    }
]


@ui.refreshable
def model_status():
    if MODEL_PATH.exists():
        from datetime import datetime
        trained_at = datetime.fromtimestamp(MODEL_PATH.stat().st_mtime).strftime('%d %b %Y, %H:%M')
        with ui.row().classes('items-center gap-2'):
            ui.icon('check_circle', size='sm').classes('text-green-400')
            ui.label(f'Model found — last trained {trained_at}').classes('text-green-400 text-sm')
    else:
        with ui.row().classes('items-center gap-2'):
            ui.icon('warning', size='sm').classes('text-yellow-400')
            ui.label('No trained model found in /data').classes('text-yellow-400 text-sm')


def show_template():
    import json
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl bg-gray-900'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('JSON Template').classes('text-lg font-bold text-white')
            ui.button(icon='close', on_click=dialog.close).props('flat round dense color=white')

        ui.label('Each entry must have a "price" and an "attributes" object with the fields below.') \
            .classes('text-gray-400 text-sm')

        ui.code(json.dumps(JSON_TEMPLATE, indent=2, ensure_ascii=False), language='json') \
            .classes('w-full text-sm')

    dialog.open()


def train_tab():
    pending_file: dict = {'raw': None, 'name': None}

    with ui.column().classes('w-full gap-4 p-4'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('Train the model').classes('text-2xl font-bold text-white')
            ui.button('View JSON template', icon='code', on_click=show_template) \
                .props('flat size=sm color=grey')

        ui.separator()

        with ui.card().classes('w-full bg-gray-800 rounded-xl p-4'):
            ui.label('Model status').classes('text-gray-400 text-xs uppercase tracking-widest mb-1')
            model_status()

        ui.label('Upload a JSON file containing your car listings, then press Train.') \
            .classes('text-gray-500 text-sm')

        file_label = ui.label('No file selected').classes('text-gray-500 text-sm italic')
        status_label = ui.label('').classes('text-sm text-center')

        async def handle_upload(e):
            raw = await e.file.read()
            if not raw:
                ui.notify('File is empty', type='negative')
                return
            pending_file['raw'] = raw
            pending_file['name'] = e.file.name
            file_label.set_text(f'Ready to train: {e.file.name}')
            file_label.classes('text-blue-400', remove='text-gray-500')
            train_btn.props(remove='disable')

        ui.upload(on_upload=handle_upload, label='Drop JSON file here or click to browse') \
            .props('accept=.json outlined') \
            .classes('w-full')

        async def start_training():
            import tempfile, json, os

            if not pending_file['raw']:
                ui.notify('Please upload a file first', type='warning')
                return

            status_label.set_text('Training... this may take a moment')
            status_label.classes('text-gray-400', remove='text-red-400 text-green-400')
            train_btn.props('loading')

            try:
                json.loads(pending_file['raw'])  # validate

                DATA_DIR.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='wb') as tmp:
                    tmp.write(pending_file['raw'])
                    tmp_path = tmp.name

                result = await run.cpu_bound(train_model, tmp_path, str(MODEL_PATH))
                os.unlink(tmp_path)

                status_label.set_text(
                    f"Done! Trained on {result['samples']} samples — "
                    f"Mean Absolute Error: EUR {result['mae']:,.0f}"
                )
                status_label.classes('text-green-400', remove='text-gray-400 text-red-400')
                model_status.refresh()
                ui.notify('Model trained successfully!', type='positive', icon='check')

            except json.JSONDecodeError:
                status_label.set_text('Invalid JSON file')
                status_label.classes('text-red-400', remove='text-gray-400 text-green-400')
                ui.notify('Could not parse JSON', type='negative')
            except Exception as ex:
                status_label.set_text(f'Error: {ex}')
                status_label.classes('text-red-400', remove='text-gray-400 text-green-400')
                ui.notify(str(ex), type='negative')

            train_btn.props(remove='loading')

        train_btn = ui.button('Train Model', icon='model_training', on_click=start_training) \
            .props('unelevated rounded size=lg color=primary disable') \
            .classes('w-full mt-2')