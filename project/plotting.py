from capture import df
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, ColumnDataSource

df["Start_str"] = df["Start"].dt.strftime("%Y-%m-%d %H:%M:%S")
df["End_str"] = df["End"].dt.strftime("%Y-%m-%d %H:%M:%S")
cds = ColumnDataSource(df)

# Postavljam parametre za dijagram
p = figure(x_axis_type='datetime', width=500, height=100, responsive=True, title="Motion Diagram")
p.yaxis.minor_tick_line_color = None
p.ygrid[0].ticker.desired_num_ticks = 1


# Dodajem polja koja ce prikazati Start/End vreme kada se kursor postavi preko dijagrama
hover = HoverTool(tooltips=[("Start", "@Start_str"), ("End", "@End_str")])
p.add_tools(hover)


# Definisem izgled diagrama (postavljam vertikalu tako da ima raspon samo od 0 do 1)
q = p.quad(left="Start", right="End", bottom=0, top=1, color='green', source=cds)

# Diagram ide u .html fajl
output_file("Diagram.html")

# Prikazujem dijagram
show(p)
