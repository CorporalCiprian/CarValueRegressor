from nicegui import ui, run
from regressor.trainer import predict as predict_price
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent.parent / 'data' / 'regressor.pkl'


def predict_tab():
    with ui.column().classes('w-full gap-4 p-4'):
        ui.label('Enter car details').classes('text-2xl font-bold text-white')
        ui.separator()

        with ui.column().classes('w-full gap-3'):
            marca       = ui.input('Brand (Marca)').props('outlined dense').classes('w-full')
            model       = ui.input('Model').props('outlined dense').classes('w-full')
            an          = ui.number('Year (An)', value=2020).props('outlined dense').classes('w-full')
            rulaj       = ui.number('Mileage (Rulaj km)', value=50000).props('outlined dense').classes('w-full')
            putere      = ui.number('Power (Putere HP)', value=115).props('outlined dense').classes('w-full')
            combustibil = ui.select(
                ['Benzina', 'Motorina', 'Hibrid', 'Electric', 'GPL'],
                label='Fuel (Combustibil)',
                value='Benzina'
            ).props('outlined dense').classes('w-full')
            cutie       = ui.select(
                ['Manuala', 'Automata'],
                label='Gearbox (Cutie de viteze)',
                value='Manuala'
            ).props('outlined dense').classes('w-full')

        result = ui.label('').classes('text-2xl font-bold text-center text-green-400 mt-2')

        async def predict():
            if not marca.value or not marca.value.strip():
                ui.notify('Please enter the Brand (Marca).', type='warning', position='top')
                return

            if not model.value or not model.value.strip():
                ui.notify('Please enter the Model.', type='warning', position='top')
                return

            result.set_text('Predicting...')
            estimate_btn.props('loading')

            car = {
                'Marca': marca.value,
                'Model': model.value,
                'An': an.value,
                'Rulaj': rulaj.value,
                'Putere': putere.value,
                'Combustibil': combustibil.value,
                'Cutie de viteze': cutie.value,
            }

            try:
                price = await run.cpu_bound(predict_price, MODEL_PATH, car)
                result.set_text(f'Estimated price: €{price:,.0f}')
            except Exception as e:
                result.set_text('Error: model not trained yet')
                ui.notify(str(e), type='negative')

            estimate_btn.props(remove='loading')

        estimate_btn = ui.button('Estimate Price', on_click=predict, icon='sell') \
            .props('unelevated rounded size=lg color=primary') \
            .classes('w-full mt-2')