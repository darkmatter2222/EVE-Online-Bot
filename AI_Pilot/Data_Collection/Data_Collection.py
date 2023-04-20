# region ----- Training Data Collector
def data_collector(self):
    combos = [
        (138, 100),
        (163, 100),
        (189, 100)
    ]
    data_root = r'O:\eve_models\training_data\unclass'
    for i in range(10):
        xy = random.choice(combos)

        perform_move_click(self.ag, pos=xy, button='left', perform_offset=True)
        pyautogui.moveTo(get_cords_with_offset(self.ag, *self.static_screen_pos['default_cords']))
        time.sleep(1)
        img = get_screen(self.ag)
        id = uuid.uuid1()
        img = img.crop((0, 0, 500, 600))
        img.save(f"{data_root}\\{id}.png")
        logger.info(f'Saved image:{id}')

# endregion