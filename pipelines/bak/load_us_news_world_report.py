def load_us_news_world_report():

    data[year] = pd.read_excel('data/USNews liberal arts 2002-2016 (1).xls',sheet_name=str(year))
        data[year]['School Name'] = data[year]['School Name'].str.replace('!','')
        if 'State' in data[year].columns:
            data[year]['State'] = data[year]['State'].str.replace('\(','').str.replace('\)','')
        df = pd.DataFrame(list(data[year]['SAT/ACT 25th-75th Percentile'].str.split('-')),columns=['SAT/ACT 25th Percentile','SAT/ACT 75th Percentile'])
        data[year] = pd.concat([data[year],df],axis=1)
        data[year] = data[year].infer_objects()
        data[year]['SAT/ACT 25th-75th Percentile Mean'] = (data[year]['SAT/ACT 25th Percentile'].astype(int)+data[year]['SAT/ACT 75th Percentile'].astype(int))/2
