import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
#from sklearn import preprocessing
from os import path as os_path
from os import pardir, sep
from sys import path as sys_path

main_dir = sep.join(os_path.realpath(__file__).split(sep)[0:-2])
out_dir = sep.join(os_path.realpath(__file__).split(sep)[0:-2] + ['output', 'plots'])
deaths_scalar = 10#120
fig_size = (13,6)
legend_pos = [0.7, 0.7]


def cases_and_deaths(pd_cases, averaged, deaths, filename):
    for plot in ['overlay']:#, 'non_overlay']:
        if plot == 'overlay':
            fig, ax1 = plt.subplots(figsize=fig_size) # figsize=(20,8), linewidth=2)
            fig.align_xlabels = True # this doesn't work...
        else:
            fig, (ax1, ax3) = plt.subplots(2, figsize=(20,8)) # figsize=(20,8), linewidth=2)
        color = 'limegreen'
        ax1.set_xlabel('date')
        ax1.set_ylabel('cases', color='darkgreen')
        ax1.plot(pd_cases.index, pd_cases["confirm"], color='limegreen', label='cases')
        ax1.tick_params(axis='y')
        ax2 = ax1.twinx()
        ax2.plot(averaged.index, averaged['confirm'], color='blue', label='cases 7 day average')#linestyle='dashed', 
        ax2.tick_params(axis='y')
        ax2.get_yaxis().set_visible(False)

        if plot == 'overlay':
            ax3 = ax1.twinx()
        ax3.set_ylabel('deaths', color='darkred')
        ax3.step(deaths.index, deaths['deaths'], where='mid', label='deaths', color='darkred')
        ax3.plot(deaths.index, deaths['deaths'], color='darkred', alpha=0.3)#'o--', 
        ax3.tick_params(axis='y')
        plt.title('cases and deaths')
        fig.legend(loc=(legend_pos))
        plt.savefig(os_path.join(main_dir, 'latest.png'))
        plt.savefig(os_path.join(out_dir, f"{filename}_.png"))
        plt.show()
        plt.close("all")


def cases_and_deaths_log_and_norm(pd_cases, averaged, deaths, filename):
    fig, ax = plt.subplots(figsize=fig_size)
    plt.title('cases and deaths (log norm)')
    ax.set_xlabel('date')
    ax.set_ylabel('cases, ', color='limegreen')
    #log_norm(pd_cases, 'confirm')
    #log_norm(averaged, 'confirm')
    #log_norm(deaths, 'deaths')
    plt.plot(pd_cases.index, pd_cases["confirm"], color='limegreen', label='cases')
    #plt.bar(pd_cases.index, pd_cases['confirm'], color='limegreen', label='cases')
    plt.plot(averaged.index, averaged['confirm'], color='blue', label='cases 7 day average')
    ax2 = ax.twinx()
    ax2.set_ylabel('deaths', color='darkred')
    ax2.plot(deaths.index, deaths['deaths'], color='darkred', label='deaths')
    ax2.tick_params(axis='y', right=True)
    fig.legend(loc=(legend_pos))
    ax.set_xlabel('date')
    ax.margins(x=0)
    ax.set_ylabel('cases, ', color='darkgreen')
    ax.set_yscale('log')
    plt.savefig(os_path.join(main_dir, 'latest_log.png'))
    plt.savefig(os_path.join(out_dir, filename + '_log.png'))
    plt.show()
    plt.close("all")


    
# def step_plot(deaths, filename):
#     plt.savefig(os_path.join(out_dir, filename + '.png'))
#     plt.show()

#def normalize(df, key="confirm"):
    # tmp_index = df.index.copy()
    # x = df.values #returns a numpy array
    # min_max_scaler = preprocessing.MinMaxScaler()
    # x_scaled = min_max_scaler.fit_transform(x)
    # tmp = []
    # for x in x_scaled:
    #     tmp.append(x[0])
    # return pd.DataFrame({key: tmp, "date":tmp_index}).set_index("date")

# def log_norm(df, col):
#     df[col] = np.log(df.copy()[col])
#     df[col] = (df[col] - 0.5 * df[col].mean())/df[col].std()