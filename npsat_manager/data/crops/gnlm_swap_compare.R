library(dplyr)

gnlm <- read.csv("C:/Users/dsx/Downloads/GNLM_LU_basic.csv")
names(gnlm) <- stringr::str_replace(names(gnlm), "DWR_CAML_Code", "GNLM_Value")
names(gnlm) <- stringr::str_replace(names(gnlm), "LU_Name", "GNLM_Name")
swat <- read.csv("C:/Users/dsx/Downloads/SWAT_LU_orig.csv")
swat <- swat[, names(swat) %in% c("CODE", "NAME", "ID")]
names(swat) <- stringr::str_replace(names(swat), "NAME", "SWAT_Name")
names(swat) <- stringr::str_replace(names(swat), "ID", "SWAT_Value")
names(swat) <- stringr::str_replace(names(swat), "CODE", "LULC")

swat_to_gnlm <- read.csv("C:/Users/dsx/Downloads/TabulateArea_SWAT_to_GNLM_50m.csv")
swat_to_gnlm <- swat_to_gnlm[,!(names(swat_to_gnlm) %in% c("OBJECTID", "VALUE_0"))]
swat_to_gnlm_long <- tidyr::gather(swat_to_gnlm, key = "GNLM_Value", value="Area", -"LULC")

# replace the word value in the rows
swat_to_gnlm_long$GNLM_Value <- as.numeric(stringr::str_replace(swat_to_gnlm_long$GNLM_Value, "VALUE_", ""))

crop_areas <- swat_to_gnlm_long  %>% dplyr::group_by(LULC)  %>% dplyr::summarise(total_crop_area=sum(Area))

stg1 <- dplyr::left_join(swat_to_gnlm_long, crop_areas, by="LULC")

# then remove all rows that are less than 1/4 of a crop's total area
stg_filtered <- stg1[stg1$Area > stg1$total_crop_area/12,]

# and join in the names
stg2 <- dplyr::left_join(stg_filtered, gnlm, by="GNLM_Value")
stg2 <- dplyr::left_join(stg2, swat, by="LULC")
