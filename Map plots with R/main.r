library(ggplot2)
theme_set(theme_bw())
library("sf")
library(rnaturalearth)

world <- ne_countries(scale = "medium", returnclass = "sf")

p <- ggplot(data = world) +
    geom_sf(aes(fill = pop_est)) +
    scale_fill_viridis_c(option = "plasma", trans = "sqrt") +
    xlab("Longitude") + ylab("Latitude") +
    ggtitle("World map")

plot(p)
