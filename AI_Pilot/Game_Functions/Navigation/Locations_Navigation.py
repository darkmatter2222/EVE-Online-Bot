from AI_Pilot.Game_Functions.Common.UI_Table_Helpers import cell_dims, cell_dims_from_list, drange, get_row_points, get_col_points, get_cells
from AI_Pilot.Control_Functions.Monitors import get_screen
from AI_Pilot.Game_Functions.Common.UI_Table_Extraction import extract_values
from AI_Pilot.Control_Functions.Mouse_Keyboard import perform_move_click
import time

def get_location_table(ag):
    y_range = get_row_points(ag.static_screen_pos['range_grid_search_location_box'],
                             ag.static_screen_pos['search_location_box_count'])
    x_range = get_col_points(ag.static_screen_pos['range_grid_search_location_box'],
                             ag.static_screen_pos['search_location_box_columns'])
    cells = get_cells(x_range, y_range)

    extract_columns = ['Name', 'click_target']

    img = get_screen(ag)

    df = extract_values(ag, img=img, cells=cells, x_range=x_range[0:2],
                          y_range=y_range, columns=extract_columns)

    return df


def dock_at_home(ag):
    df = get_location_table(ag)

    click_target = df[df['Name'] == 'Home']['click_target'][0]
    # TODO  Handle this error if record missing!

    perform_move_click(ag=ag, pos=click_target, button='right', perform_offset=False)
    time.sleep(0.1)
    click_target = (click_target[0] + 70, click_target[1] + 27)
    perform_move_click(ag=ag, pos=click_target, button='left', perform_offset=False)
    time.sleep(60)





