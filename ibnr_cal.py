import pandas as pd
from pandas import DataFrame


def read_data(path):
    if path.split(".")[-1] in ['xlsx','xls']:
        data=pd.read_excel(path)
    else:
        data=pd.read_csv(path,engine='python',encoding='gbk')
    import datetime

    data['occur_month'] = data['occur_month'].map(lambda x: datetime.datetime.strftime(x, '%Y年%m月'))
    data['acc_close'] = data['acc_close'].map(lambda x: ('%.0f') % x)
    data['cntr_year'] = data['cntr_year'].map(lambda x: ('%.0f') % x)
    data['pay_amnt']=data['pay_amnt'].map(lambda x: ('%.2f') % x)

    ret_dict={}
    ret_dict['shapex']=data.shape[0]
    ret_dict['shapey'] = data.shape[1]
    ret_dict['head_table'] = data.head(20).to_dict(orient='records')
    ret_dict['datemax']=data['occur_month'].max()
    ret_dict['datemin'] = data['occur_month'].min()

    counts = data['cntr_year'].value_counts()
    tmp = DataFrame([counts.index.tolist(), counts.values.tolist()]).T
    tmp.columns = ['cntr_year', 'counts']
    ret_dict['cntr_years']=tmp.to_dict(orient='record')
    return ret_dict






def get_triangle(df, index, columns, values, aggfunc):
    '''
    生成三角标准的三角形
    :param df:
    :param index:出险月的列名称
    :param columns:进展月的列名称，一般是acc_close或development_month
    :param values:需要累加的列的名称，如果算费用三角形就是费用，如果算次数三角形就是次数
    :param aggfunc:Pivot操作时的agg函数，一般用sum
    :return:(ori_triangle,triangle),ori_triangle直接生成的三角形，triangle为标准化的三角形
    '''
    # 生成三角形
    triangle = df.pivot_table(index=index, columns=columns, values=values, aggfunc=aggfunc).sort_index()
    ori_triangle = triangle.copy()
    # 标准化三角形为N*N
    date_min = triangle.index[0]
    date_max = triangle.index[-1]
    print('from : ', date_min.strftime('%Y%m'))
    print('to : ', date_max.strftime('%Y%m'))
    total_year = date_max.year - date_min.year
    total_month = total_year * 12 + (date_max.month - date_min.month) + 1
    edge_num = max(total_month, len(triangle.columns))
    print('month num : ', total_month)
    print('development month max :', triangle.columns[-1])
    std_str_index = [
        str(date_min.year + int((date_min.month + i - 1) / 12)) + str((date_min.month + i - 1) % 12 + 1).zfill(2) for i
        in range(edge_num)]

    str_index = triangle.index.to_series().apply(lambda t: t.strftime("%Y%m")).values
    triangle.index = str_index
    triangle = triangle.reindex(std_str_index).T
    triangle = triangle.reindex(range(edge_num)).T
    triangle.fillna(0, inplace=True)
    return ori_triangle, triangle


def get_acc_triangle(triangle):
    '''
    生成累加三角形
    :param triangle: 一般是get_triangle产生的三角形
    :return:
    '''
    acc_triangle = triangle.copy()
    for i in range(len(acc_triangle)):
        for j in range(1, len(acc_triangle)):
            if j <= len(acc_triangle) - i - 1:
                acc_triangle.iloc[i, j] = acc_triangle.iloc[i, j - 1] + acc_triangle.iloc[i, j]
    return acc_triangle


def get_factor(acc_triangle, factor_month_num=None):
    '''
    根据累计三角形产生因子
    :param acc_triangle:累计三角形，标准N*N形状
    :param factor_month_num:在各个进展月上计算因子时使用的月的个数,如果最后几个进展月不满足计算量条件，补充nan；如果为None,则用所有数据计算
    :return:
    '''
    factor = []
    if factor_month_num is None:
        for i in range(1, acc_triangle.shape[1]):
            asum = acc_triangle.iloc[:, i].sum()
            bsum = acc_triangle.iloc[:-i, i - 1].sum()
            if bsum == 0:
                factor.append(0)
            else:
                factor.append(asum / bsum)
    else:
        for i in range(1, acc_triangle.shape[1] - factor_month_num + 1):
            asum = acc_triangle.iloc[len(acc_triangle) - i - factor_month_num:len(acc_triangle) - i, i].sum()
            bsum = acc_triangle.iloc[len(acc_triangle) - i - factor_month_num:len(acc_triangle) - i, i - 1].sum()
            if bsum == 0:
                factor.append(0)
            else:
                factor.append(asum / bsum)
        if len(factor) < len(acc_triangle):
            factor += [None for _ in range(len(acc_triangle) - len(factor) - 1)]
    return factor


def get_est_triangle(triangle, acc_triangle, factor):
    '''
    根据因子返回估计三角形及估计的累计三角形
    :param triangle:
    :param acc_triangle:
    :param factor:
    :return:
    '''
    est_acc_triangle = acc_triangle.copy()
    for i in range(0, len(est_acc_triangle)):
        for j in range(len(est_acc_triangle) - i, est_acc_triangle.shape[1]):
            est_acc_triangle.iloc[i, j] = est_acc_triangle.iloc[i, j - 1] * factor[j - 1]

    est_triangle = triangle.copy()
    for i in range(0, len(est_triangle)):
        for j in range(len(est_acc_triangle) - i, est_triangle.shape[1]):
            est_triangle.iloc[i, j] = est_acc_triangle.iloc[i, j] - est_acc_triangle.iloc[i, j - 1]
    return est_triangle, est_acc_triangle


#
# def get_average_fee(average_fee_triangle,std_fee,replace_start,replace_min,fee_month_num=None):
#     fee=[]
#     fee_adjust=[]
#     if fee_month_num is None:
#         fee=average_fee_triangle.mean().values.tolist()
#     else:
#         for i in range(0, average_fee_triangle.shape[1] - fee_month_num):
#             s= acc_triangle.iloc[len(acc_triangle) - i - factor_month_num:len(acc_triangle) - i, i].mean()
#             fee.append(s)
#
#     for i in range(0,average_fee_triangle.shape[1]):
#         if i<min(replace_start, average_fee_triangle.shape[1] - replace_min-1):
#             fee_adjust.append(fee[i])
#         elif i<len(std_fee):
#             fee_adjust.append(std_fee[i])
#         else:
#             fee_adjust.append(std_fee[-1])
#     fee+=[fee[-1] for _ in range(len(fee_adjust)-len(fee))]
#     return fee,fee_adjust


def get_est_fee_triangle(fee_triangle, est_count_triangle, fee):
    est_fee_triangle = fee_triangle.copy()
    for i in range(0, len(est_fee_triangle)):
        for j in range(len(est_fee_triangle) - i, est_fee_triangle.shape[1]):
            est_fee_triangle.iloc[i, j] = est_count_triangle.iloc[i, j] * fee[j]

    est_acc_fee_triangle = fee_triangle.copy()
    for i in range(0, len(est_fee_triangle)):
        for j in range(1, est_acc_fee_triangle.shape[1]):
            est_acc_fee_triangle.iloc[i, j] = est_fee_triangle.iloc[i, j] + est_acc_fee_triangle.iloc[i, j - 1]

    return est_fee_triangle, est_acc_fee_triangle


def get_ibnr(acc_triangle):
    '''

    :param acc_triangle:
    :return:
    '''
    ibnr = []
    for i in range(len(acc_triangle) - 1, 0, -1):
        total = acc_triangle.iloc[i, -1]
        closest = acc_triangle.iloc[i, len(acc_triangle) - 1 - i]
        ibnr.append(total / closest)
    return ibnr