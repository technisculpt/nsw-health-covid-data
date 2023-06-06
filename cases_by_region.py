import pandas as pd    
import timeit

# add lat lng information to nsw health data for mapping purposes

'''
postcode, locality, state, long, lat, dc, type, status, sa3, sa3name, sa4, sa4name, region, Lat_precise, Long_precise,
SA1_MAINCODE_2011, SA1_MAINCODE_2016, SA2_MAINCODE_2016, SA2_NAME_2016, SA3_CODE_2016, SA3_NAME_2016, SA4_CODE_2016,
SA4_NAME_2016, RA_2011, RA_2016, MMM_2015, MMM_2019, ced, altitude, chargezone, phn_code, phn_name, lgaregion, lgacode,
electorate, electoraterating
''' 
def main():
    nsw_postcodes = './datasets/data/nsw_postcodes.csv'
    nsw_pc = pd.read_csv(filepath_or_buffer=nsw_postcodes, index_col=0)
    csv_file = '20220120-20230426'
    pc_cases = pd.read_csv(filepath_or_buffer=f"output/{csv_file}_postcodes.csv", parse_dates=["date"], index_col=0)
    pd_pc = pd.read_csv(filepath_or_buffer=f"output/{csv_file}_postcodes_sorted.csv", parse_dates=["date"], index_col=0)

    # pd_pc["2045"].to_csv(path_or_buf=f"output/{csv_file}_haberfield.csv")
    # pd_pc["2045"].cumsum().to_csv(path_or_buf=f"output/{csv_file}_haberfield_cumsum.csv")
    # pd_pc["2222"].to_csv(path_or_buf=f"output/{csv_file}_penshurst.csv")
    # pd_pc["2222"].cumsum().to_csv(path_or_buf=f"output/{csv_file}_penshurst_cumsum.csv")

    postcodes = []
    for i in range(len(pc_cases)):
        postcode = pc_cases['postcode'][i]
        if postcode not in postcodes:
            postcodes.append(postcode)

    tmp_pcs = []
    nsw = {}
    for item in nsw_pc.values:
        if item[2] == 'NSW' and str(item[0]) in postcodes:
            if str(item[0]) not in tmp_pcs:
                tmp_pcs.append(str(item[0]))
                nsw[str(item[0])] = {'region': item[11],'lng': item[13],'lat': item[14]}

    regions = []
    latlngs = []
    nsw_pc = []
    for item in nsw:
        if nsw[item]['region'] not in regions:
            regions.append(nsw[item]['region'])
            latlngs.append([nsw[item]['lat'], nsw[item]['lng']])
            nsw_pc.append([])

    it = 0
    for item in nsw:
        if nsw[item]['region'] == regions[it]:
            nsw_pc[it].append(item)
        else:
            nsw_pc[it + 1].append(item)
            it += 1
            if it == (len(regions) - 1):
                break
    
    cols = []
    data = []
    for reg in range(len(regions)):
        cols.append(regions[reg])
        new_reg = True
        tmp_pc = ''
        for col in pd_pc:
            if str(col) in nsw_pc[reg]:
                if new_reg:
                    tmp_pc = pd_pc[col]
                    new_reg = False
                else:
                    tmp_pc += pd_pc[col]
        data.append(tmp_pc)

    local_scope = locals()
    out_str = ""

    region_cases = pd.DataFrame()
    local_scope["pd"] = pd
    local_scope['date'] = pd_pc.index
    local_scope['region_cases'] = region_cases

    for d in range(len(data)):
        local_scope[f"reg{str(d)}"] = data[d]
        out_str += f"'{cols[d]}': reg{str(d)}, "
    out_str = out_str[0:-1]

    exec_str = "region_cases = pd.DataFrame({" + out_str + " 'date':" + " pd_pc.index }).set_index('date')"
    exec(exec_str, local_scope)

    region_cases = local_scope['region_cases']
    region_cases.to_csv(path_or_buf=f"output/{csv_file}_by_region.csv")
    region_cases.to_csv(path_or_buf=f"output/{csv_file}_by_region.csv")
    region_cases.cumsum().to_csv(path_or_buf=f"output/{csv_file}_by_region_cumsum.csv")


if __name__ == "__main__":

    result = timeit.timeit(stmt=f"main()", globals=globals(), number=1)
    print(f"Execution time is {result / 1} seconds")
