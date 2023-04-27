from AI_Pilot.Game_Functions.Common.UI_Table_Helpers import cell_dims, cell_dims_from_list, drange, get_row_points, get_col_points, get_cells
from AI_Pilot.Control_Functions.Monitors import get_screen
from AI_Pilot.Game_Functions.Common.UI_Table_Extraction import extract_values

def set_destination(ag, name):
    pass

    y_range = get_row_points(ag.static_screen_pos['range_grid_search_location_box'],
                             ag.static_screen_pos['search_location_box_count'])
    x_range = get_col_points(ag.static_screen_pos['range_grid_search_location_box'],
                             ag.static_screen_pos['search_location_box_columns'])
    cells = get_cells(x_range, y_range)

    extract_columns = ['Name', 'click_target']

    img = get_screen(ag)

    return extract_values(ag, img=img, cells=cells, x_range=x_range[0:2],
                          y_range=y_range, columns=extract_columns,
                          monitor_x_offset=self.config['monitor_offset_x'],
                          monitor_y_offset=self.config['monitor_offset_y'],
                          click_target_offset_x=self.config['click_target_offset_x'],
                          click_target_offset_y=self.config['click_target_offset_y'])



    def get_location_data(self, rows=13, refresh_screen=False):
        y_range = get_row_points(self.config['locations_box'], rows)
        x_range = get_col_points(self.config['locations_box'], self.config['locations_box_columns'])
        cells = get_cells(x_range[0:2], y_range)

        if refresh_screen:
            self.screen = self.get_screen()

        extract_columns = ['Name', 'click_target']

