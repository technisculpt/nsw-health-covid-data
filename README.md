# the NSW health case API is deprecated.

For up to date information consult the fortnightly NSW [**respiratory surveillance**](https://www.health.nsw.gov.au/Infectious/covid-19/Pages/reports.aspx) or the [**federal reporting**](https://www.health.gov.au/topics/covid-19/reporting) 

# nsw-health-covid-data

aggregate data from different sources into easy to access .csv files

[**nsw_health_master.csv**](https://github.com/technisculpt/nsw-health-covid-data/blob/main/output/nsw_health_master.csv) - raw data from [nsw health api](https://data.nsw.gov.au/data/api/1/util/snippet/api_info.html?resource_id=5d63b527-e2b8-4c42-ad6f-677f14433520) (individual cases/clusters released weekly)

[**dates_cases.csv**](https://github.com/technisculpt/nsw-health-covid-data/blob/main/output/dates_cases.csv) - cases per day (above filtered to a per day time series)

[**website_stats.csv**](https://github.com/technisculpt/nsw-health-covid-data/blob/main/output/website.csv) - deaths, hospitilizations, ICU, pcr cases, rat cases and total cases as [reported weekly](https://www.health.nsw.gov.au/Infectious/covid-19/Pages/stats-nsw.aspx)

[**deaths.csv**](https://github.com/technisculpt/nsw-health-covid-data/blob/main/output/deaths.csv) - deaths taken from the [surveillance reports](https://www.health.nsw.gov.au/Infectious/covid-19/Pages/weekly-reports.aspx) up until 2023-04-29 and a combination of the website and twitter after

[**pdf_deaths.csv**](https://github.com/technisculpt/nsw-health-covid-data/blob/main/output/pdf_deaths.csv) - deaths taken only from the [surveillance reports](https://www.health.nsw.gov.au/Infectious/covid-19/Pages/weekly-reports.aspx) **(deprecated)**

![alt text](https://github.com/technisculpt/nsw-health-covid-data/blob/main/latest.png)

![alt text](https://github.com/technisculpt/nsw-health-covid-data/blob/main/latest_log.png)
