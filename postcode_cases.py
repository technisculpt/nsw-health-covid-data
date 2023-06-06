import pandas as pd    
import timeit

# make .csvs for individual postcodes

def cumsum():
    csv_file = '20220120-20230426'
    pc_cases = pd.read_csv(filepath_or_buffer=f"output/{csv_file}_postcodes_sorted.csv", parse_dates=["date"], index_col=0)
    pc_cases.cumsum().to_csv(path_or_buf=f"output/{csv_file}_postcodes_cumulative_sorted.csv")

def main():
    csv_file = '20220120-20230426'
    pc_cases = pd.read_csv(filepath_or_buffer=f"output/{csv_file}_postcodes.csv", parse_dates=["date"], index_col=0)
    date_ptr = pc_cases["date"][0].date()

    postcodes = []
    for i in range(len(pc_cases)):
        postcode = pc_cases['postcode'][i]
        if postcode not in postcodes:
            postcodes.append(postcode)

    zero_day = {}
    for pc in postcodes:
        if pc not in zero_day:
            zero_day[pc] = 0

    it_df = 0
    process_postcodes = True
    dict_list = []
    while(process_postcodes):

        day_dict = {}
        if date_ptr != pc_cases["date"][it_df].date():
            dict_list.append(zero_day)
        else:
            while(date_ptr == pc_cases["date"][it_df].date() and process_postcodes):
                postcode = pc_cases["postcode"][it_df]
                cases = pc_cases["cases"][it_df]

                if postcode not in day_dict:
                    day_dict[postcode] = cases
                else:
                    day_dict[postcode] += cases

                it_df += 1
                if it_df == len(pc_cases) - 1:

                    dict_list.append(day_dict)
                    
                    for pc in postcodes:
                        if pc not in day_dict:
                            day_dict[pc] = 0

                    process_postcodes = False

            for pc in postcodes:
                if pc not in day_dict:
                    day_dict[pc] = 0
            dict_list.append(day_dict)
        date_ptr += pd.Timedelta(days=1)
    date_ptr = pc_cases["date"][0].date()

    local_namespace = locals()
    dates = []

    for pc in postcodes: # generate dynamic postcode lists
        exec(f"_{pc} = []", local_namespace)

    for day in dict_list: # sort API data into said lists
        for pc in postcodes:
            exec(f"_{pc}.append({day[pc]})", local_namespace)
        dates.append(pd.to_datetime(date_ptr))
        date_ptr += pd.Timedelta(days=1)

    pc_str = "'date': dates"
    for pc in postcodes:
        pc_str += f", '{pc}': _{pc}"

    data_str = pc_str

    local_namespace['pd'] = pd
    local_namespace['dates'] = dates
    pd_exec = f"post_codes_sorted = pd.DataFrame({{{data_str}}}).set_index('date')"
    exec(pd_exec, local_namespace)

    post_codes_sorted = local_namespace['post_codes_sorted']
    post_codes_sorted.to_csv(path_or_buf=f"output/{csv_file}_postcodes_sorted.csv")

if __name__ == "__main__":

    result = timeit.timeit(stmt=f"cumsum()", globals=globals(), number=1)
    print(f"Execution time test1 is {result / 1} seconds")
