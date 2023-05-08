from AI_Pilot.Game_Functions.Common.UI_Table_Helpers import cell_dims, cell_dims_from_list, drange, get_row_points, get_col_points, get_cells
from AI_Pilot.Control_Functions.Monitors import get_screen
from AI_Pilot.Game_Functions.Common.UI_Table_Extraction import extract_values
from loguru import logger

def get_assets_search_table(ag):
    y_range = get_row_points(ag.static_screen_pos['range_grid_search_assets_box'],
                             ag.static_screen_pos['search_assets_box_count'])
    x_range = get_col_points(ag.static_screen_pos['range_grid_search_assets_box'],
                             ag.static_screen_pos['search_assets_box_columns'])
    cells = get_cells(x_range, y_range)

    extract_columns = ['Name', 'click_target']

    img = get_screen(ag)

    df = extract_values(ag, img=img, cells=cells, x_range=x_range[0:2],
                          y_range=y_range, columns=extract_columns)

    logger.info('Locations:')
    logger.info(df)

    return df


def get_set_dest_options(ag, img):
    # region ----- get gav options
    nav_result = ag.up.predict(img, 'set_dest')
    logger.info(nav_result)
    # endregion
    return nav_result