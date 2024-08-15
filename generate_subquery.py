def table2sampleid(table_name):
    t2sid = {
        'title': 'tid',
        'cast_info': 'ciid',
        'movie_companies': 'mcid',
        'movie_info_idx': 'miiid',
        'movie_info': 'miid',
        'movie_keyword': 'mkid'
        }
    return t2sid[table_name]

def ali2table(ali):
    a2t = {
        't': 'title',
        'ci': 'cast_info',
        'mc': 'movie_companies',
        'mi_idx': 'movie_info_idx',
        'mi': 'movie_info',
        'mk': 'movie_keyword',
        'title': 'title',
        'cast_info': 'cast_info',
        'movie_companies': 'movie_companies',
        'movie_info_idx': 'movie_info_idx',
        'movie_info': 'movie_info',
        'movie_keyword': 'movie_keyword'
    }
    return a2t[ali]

csv_file = open('job-light-ranges_mm_wisdm_mscn.csv', 'r')
#sql_file = open('job-light-ranges_mm_wisdm_deepdb.sql', 'r')
csv_lines = csv_file.readlines()
#sql_lines = sql_file.readlines()
sub_dir = './mscn_subquery/'
for i, line in enumerate(csv_lines):
    outfile = open(sub_dir + 'q' + str(i) + '.csv', 'w')
    tables = line.split('#')[0].split(',')
    joins = line.split('#')[1].split(',')
    predicates = line.split('#')[2].split(',')
    result = line.split('#')[3]
    num_tables = len(tables)
    for k in range(2**num_tables):
        csv_str = ''
        tmp_tables = []
        for l in range(num_tables):
            if (k >> l) % 2 == 1:
                tmp_tables.append(tables[l])
        if len(tmp_tables) <  2:
            continue
        for t in tmp_tables:
            csv_str += (t + ',')
        csv_str = csv_str[:-1] + '#'
        for j in joins:
            t_c0 = j.split('=')[0]
            t_c1 = j.split('=')[1]
            t0 = t_c0.split('.')[0]
            t1 = t_c1.split('.')[0]
            if t0 in tmp_tables and t1 in tmp_tables:
                csv_str += j + ','
        if csv_str[-1] == ',':
            csv_str = csv_str[:-1] +  '#'
        else:
            continue
        for j in range(0, len(predicates), 3):
            t_col = predicates[j]
            op = predicates[j + 1]
            val = predicates[j + 2]
            t = t_col.split('.')[0] 
            if t in tmp_tables:
                csv_str += (t_col + ',' + op + ',' + val + ',')
        if csv_str[-1] == ',':
            csv_str = csv_str[:-1] + '#' + result 
        else:
            csv_str += ('#' + result)
        outfile.write(csv_str)
    outfile.close()
