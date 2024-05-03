# install.packages("tidyverse")
# install.packages("ggbeeswarm")
# install.packages("xtable")
# install.packages("gridExtra")
# install.packages("cowplot")

library(tidyverse)
library(ggbeeswarm) # centered geom_jitter
library(xtable)
library(gridExtra)
library(cowplot)

# floorYear <- function(x) (x %/% 10) * 10
get_year <- function(x) as.integer(str_sub(as.character(x), end = 4))
# add_cite <- function(x) str_c(r"(//)", 'cite//{', x, "//}" )
reorder_factor <- function(x, y) stats::reorder(`x`, -y)

path <- "YOUR_PATH_HERE/"

systreviewdims <-  readxl::read_excel(str_c(path, "provenance_corpus_papers.xlsx"),
                                      sheet = "Sheet1",
                                      col_names = FALSE) %>% t()

colnames(systreviewdims) <- systreviewdims[1,]
colnames(systreviewdims)[1] <- "Record"

BASESIZE = 12
DOTSIZE = 0.47
STACKRATIO = 1.1

POSNUDGE1 = 0.49
POSNUDGE2 = 0.49
POSNUDGE3 = 0.43

systreviewdims <- systreviewdims[-1,] %>% 
  as.data.frame() %>% 
  filter(Accepted=="1") %>% 
  mutate_at("year", as.integer) %>% 
  # mutate(decade = floorYear(year)) %>% 
  mutate_all(as.factor) %>% 
  mutate(Year = year) %>% 
  select(!(year))

p_gen <- systreviewdims %>% 
  filter(`Literature Provenance` == "general data") %>% 
  mutate(`Medical Application` = case_when(`Application Area` != "non-life-science" ~ "life science",
                                           .default = "non-life science")) %>% 
  mutate(Year = as.POSIXct(ymd(Year, truncated = 2L))) %>% 
  mutate(Year = get_year(Year)) %>%  
  mutate(`Literature Provenance` = forcats::fct_inorder(`Literature Provenance`)) %>% 
  ggplot(aes(x = Year, 
             y = reorder_factor(`Literature Provenance`, -Year), #  to get general on top, then big data then ML
             shape = reorder_factor(`Medical Application`, -Year),
             fill = reorder_factor(`Medical Application`, -Year),
             col = reorder_factor(`Medical Application`, -Year)
  )
  ) +
  theme_bw(base_size = BASESIZE) +
  geom_dotplot(stackgroups = TRUE,
               method = "dotdensity",
               binpositions = "all",
               binwidth = 0.9,
               stackratio = STACKRATIO,
               position = position_nudge(y=POSNUDGE1),
               dotsize = DOTSIZE,
               ) +
  # coord_flip() +
  scale_x_continuous(breaks = 1993:2024,
                     minor_breaks = 1,
                     limits = c(1993,2024),
                     labels = NULL) +
  theme(
    axis.text.x=element_blank(),
    axis.ticks = element_blank(),
    axis.ticks.x=element_blank(),
    legend.position="none",
    legend.title = element_blank(),
    panel.grid.major.y = element_blank()
  ) +
  scale_shape_manual(values=c(17,23))+
  scale_color_manual(values = c( "#66B2FF", "red3"))+
  scale_fill_manual(values =  c( "#66B2FF", "red3")) +
  # guides(shape = guide_legend(reverse = T),
  #        col = guide_legend(reverse = T),
  #        fill = guide_legend(reverse = T)) +
  labs(y= "", x= "")

p_big <- systreviewdims %>% 
  filter(`Literature Provenance` == "big data") %>%
  mutate(`Medical Application` = case_when(`Application Area` != "non-life-science" ~ "life science",
                                           .default = "non-life science")) %>% 
  mutate(Year = as.POSIXct(ymd(Year, truncated = 2L))) %>% 
  mutate(Year = get_year(Year)) %>%  
  mutate(`Literature Provenance` = forcats::fct_inorder(`Literature Provenance`)) %>% 
  ggplot(
    aes(x = Year,
             y = reorder_factor(`Literature Provenance`, -Year), #  to get general on top, then big data then ML
             shape = reorder_factor(`Medical Application`, -Year),
             fill = reorder_factor(`Medical Application`, -Year),
             col = reorder_factor(`Medical Application`, -Year)
  )
  ) +
  theme_bw(base_size = BASESIZE) +
  geom_dotplot(stackgroups = TRUE,
               method = "dotdensity",
               stackdir = "up",
               binpositions = "all",
               stackratio = STACKRATIO,
               dotsize = DOTSIZE,
               position = position_nudge(y=POSNUDGE2),
               binwidth = 0.9
  ) +
  scale_x_continuous(breaks = 1993:2024,
                     minor_breaks = 1,
                     limits = c(1993,2024),
                     labels=NULL) +
  theme(
    axis.text.x=element_blank(),
    axis.ticks.x=element_blank(),
    axis.ticks = element_blank(),
    # axis.title.y = element_text(margin = margin(r = -20)),
    legend.position = "none",
    legend.title = element_blank(),
    panel.grid.major.y = element_blank(),
  ) +
  scale_color_manual(values = c( "#66B2FF", "red3"))+
  scale_fill_manual(values =  c( "#66B2FF", "red3")) +
  scale_shape_manual(values=c(17,23))+
  # scale_color_manual(values = c( "#F8766D", "#00BFC4"))+
  # scale_fill_manual(values =  c( "#F8766D", "#00BFC4")) +
  # guides(shape = guide_legend(reverse = T),
  #        col = guide_legend(reverse = T),
  #        fill = guide_legend(reverse = T)) +
  labs(y= "", x = "")
# p_big

p_ml <- systreviewdims %>% 
  filter(`Literature Provenance` == "ML data") %>% 
  mutate(`Medical Application` = case_when(`Application Area` != "non-life-science" ~ "life science",
                                           .default = "non-life science")) %>% 
  mutate(Year = as.POSIXct(ymd(Year, truncated = 2L))) %>% 
  mutate(Year = get_year(Year)) %>%  
  mutate(`Literature Provenance` = forcats::fct_inorder(`Literature Provenance`)) %>% 
  ggplot(aes(x = Year, 
             y = reorder_factor(`Literature Provenance`, -Year), #  to get general on top, then big data then ML
             shape = reorder_factor(`Medical Application`, -Year),
             fill = reorder_factor(`Medical Application`, -Year),
             col = reorder_factor(`Medical Application`, -Year)
  )
  ) +
  theme_bw(base_size = BASESIZE) +
  geom_dotplot(stackgroups = TRUE,
               method = "dotdensity",
               stackdir = "up",
               binwidth = 0.9,
               dotsize = DOTSIZE,
               stackratio = STACKRATIO,
               drop=FALSE,
               position = position_nudge(y=POSNUDGE3),
               binpositions = "all"
  ) +
  scale_x_continuous(breaks = 1993:2024,
                     minor_breaks = 1,
                     limits = c(1993,2024)
  ) +
  
  scale_shape_manual(values=c(17,23))+
  scale_color_manual(values = c( "#66B2FF", "red3"))+
  scale_fill_manual(values =  c( "#66B2FF", "red3")) +
  # scale_color_manual(values = c( "#F8766D", "#00BFC4"))+
  # scale_fill_manual(values =  c( "#F8766D", "#00BFC4")) +
  guides(shape = guide_legend(reverse = T),
         col = guide_legend(reverse = T),
         fill = guide_legend(reverse = T)) +
  theme(axis.text.x = element_text(angle = 60, hjust = 1),
        axis.ticks = element_blank(),
        panel.grid.major.y = element_blank(),
        legend.direction = "horizontal",
        legend.position="bottom",
        legend.title = element_blank(),
        legend.box.spacing = unit(-0.3, "pt")
  ) +
  labs(y= "                                   data category",
       x = "year")

plot_grid(p_gen, 
          NULL,
          p_big, 
          NULL,
          p_ml, 
          ncol = 1, 
          rel_heights = c(0.33,
                          -0.085,
                          0.33, 
                          -0.09,
                          0.8),
          label_y = "abc",
          align = "v",
          axis = "x")
##################################################################
# Save (optional)
ggsave(str_c(path, "LitProvOverYearsLifeScience.pdf"), width = 20, height = 8*1.4, units = "cm")
