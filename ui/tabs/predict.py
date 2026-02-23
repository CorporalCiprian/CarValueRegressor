from nicegui import ui


def predict_tab():
    with ui.column().classes('w-full gap-4 p-4'):
        ui.label('Enter car details').classes('text-2xl font-bold text-white')
        ui.separator()

        with ui.column().classes('w-full gap-3'):
            year    = ui.number('Year', value=2020).props('outlined dense').classes('w-full')
            mileage = ui.number('Mileage (km)', value=50000).props('outlined dense').classes('w-full')
            engine  = ui.number('Engine size (L)', value=1.6).props('outlined dense').classes('w-full')

        result = ui.label('').classes('text-2xl font-bold text-center text-green-400 mt-2')

        def predict():
            result.set_text('Estimated price: $...')

        ui.button('Estimate Price', on_click=predict, icon='sell') \
            .props('unelevated rounded size=lg color=primary') \
            .classes('w-full mt-2')