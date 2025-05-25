import pandas as pd

def color_returns(val):
    if pd.isna(val):
        return ""
    elif val > 0:
        return "color: mediumseagreen"
    elif val < 0:
        return "color: orangered"
    else:
        return ""
