import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
#from sklearn import preprocessing
from os import path as os_path
from os import pardir, sep
from sys import path as sys_path

out_dir = sep.join(os_path.realpath(__file__).split(sep)[0:-2] + ['output'])
deaths_scalar = 10#120

def step_plot(deaths, filename):
    plt.savefig(os_path.join(out_dir, filename + '.png'))
    plt.show()

def normalize(df):
#def normalize(df, key="confirm"):
    # tmp_index = df.index.copy()
    # x = df.values #returns a numpy array
    # min_max_scaler = preprocessing.MinMaxScaler()
    # x_scaled = min_max_scaler.fit_transform(x)
    # tmp = []
    # for x in x_scaled:
    #     tmp.append(x[0])
    # return pd.DataFrame({key: tmp, "date":tmp_index}).set_index("date")
    #return (df - 0.5 * df.mean())/df.std()
    return (df - 0.5 * df.mean())/df.std()

def cases_and_deaths(pd_cases, averaged, deaths, filename):
    for plot in ['overlay', 'non_overlay']:
        if plot == 'overlay':
            fig, ax1 = plt.subplots(figsize=(20,8)) # figsize=(20,8), linewidth=2)
            fig.align_xlabels = True # this doesn't work...
        else:
            fig, (ax1, ax3) = plt.subplots(2, figsize=(20,8)) # figsize=(20,8), linewidth=2)
        color = 'limegreen'
        ax1.set_xlabel('date')
        ax1.set_ylabel('cases', color='darkgreen')
        ax1.plot(pd_cases.index, pd_cases["confirm"], color='limegreen', label='cases')
        ax1.tick_params(axis='y')
        ax2 = ax1.twinx()
        color = 'lime'#'lightgreen'
        ax2.plot(averaged.index, averaged['confirm'], color=color, linestyle='dashed', label='cases average')#dashed
        ax2.tick_params(axis='y')
        ax2.get_yaxis().set_visible(False)

        if plot == 'overlay':
            ax3 = ax1.twinx()
        ax3.set_ylabel('deaths', color='darkred')
        ax3.step(deaths.index, deaths['deaths'], where='mid', label='deaths', color='darkred')
        ax3.plot(deaths.index, deaths['deaths'], 'o--', color='darkred', alpha=0.3)
        ax3.tick_params(axis='y')
        plt.title('NSW Covid Statistics')
        fig.legend(loc=([0.8, 0.7]))
        plt.savefig(os_path.join(out_dir, filename + '_' + plot + '.png'))
        plt.show()
        plt.close("all")

def cases_and_deaths_log_and_norm(pd_cases, averaged, deaths, filename):
    plt.close("all")
    legend_pos = [0.6, 0.75]
    figure_size = (10,6)
    fig, ax = plt.subplots(figsize=figure_size)
    plt.title('cases and deaths')
    ax.set_xlabel('date')
    ax.set_ylabel('cases, ', color='darkgreen')
    plt.bar(pd_cases.index, pd_cases['confirm'], color='lightgreen', label='cases')
    plt.plot(averaged.index, averaged['confirm'], color='red', label='cases 7 day average')
    ax2 = ax.twinx()
    deaths['deaths'] = np.log(deaths.copy()['deaths']) # TODO this shouldn't be here!
    deaths0 = normalize(deaths, "deaths")
    ax2.set_ylabel('deaths', color='black')
    ax2.plot(deaths0.index, deaths0['deaths'], color='black', label='deaths')
    ax2.tick_params(axis='y', right=True)
    fig.legend(loc=(legend_pos))
    plt.title('cases (log transform & normalised) and deaths')
    ax.set_xlabel('date')
    ax.margins(x=0)
    ax.set_ylabel('cases, ', color='darkgreen')

    # log + normal
    plt.bar(pd_cases.index, pd_cases['confirm'], color='lightgreen', label='cases  (log/scale)')
    plt.plot(averaged.index, averaged['confirm'], color='red', label='cases  (avg/log/scale)')
    ax2 = ax.twinx()
    deaths['deaths'] = np.log(deaths.copy()['deaths']) # TODO this shouldn't be here!
    deaths0 = normalize(deaths, "deaths")
    ax2.set_ylabel('deaths', color='black',)
    ax2.plot(deaths0.index, deaths0['deaths'], color='black', label='deaths')
    ax.set_yscale('log')
    ax.set_yticklabels(pd_cases['confirm'])
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax2.set_yticklabels(deaths['deaths'])
    fig.legend(loc=(legend_pos))
    plt.savefig(os_path.join(out_dir, filename + '_cases_log.png'))
    plt.show()

def generate_plots(pd_cases, averaged, filename):
    plt.close("all")
    legend_pos = [0.6, 0.67]
    figure_size = (7,6)
    fig, ax = plt.subplots(figsize=figure_size)
    plt.title('cases')
    ax.set_xlabel('date')
    ax.margins(x=0)
    ax.set_ylabel('cases, ', color='darkgreen')
    
    plt.bar(pd_cases.index, pd_cases['confirm'], color='lightgreen', label='daily cases')
    plt.plot(averaged.index, averaged['confirm'], color='darkred', label='cases average')
    #plt.plot(averaged.index, averaged['pcr'], color='red', label='PCR test')
    #plt.plot(averaged.index, averaged['rat'], color='orange', label='RAT test')

    fig.legend(loc=(legend_pos))
    plt.savefig(os_path.join(out_dir, filename + '.png'))
    plt.show()
    plt.close("all")

# log + normalise
def generate_plots_log_normal(pd_cases, averaged, filename):
    plt.close("all")
    legend_pos = [0.6, 0.67]
    figure_size = (7,6)
    fig, ax = plt.subplots(figsize=figure_size)
    plt.title('cases log transform & normalised')
    ax.set_xlabel('date')
    ax.margins(x=0)
    ax.set_ylabel('cases, ', color='darkgreen')

    pd_cases['confirm'] = np.log(pd_cases['confirm'])
    averaged['confirm'] = np.log(averaged['confirm'])
    pd_cases1 = normalize(pd_cases.copy())
    averaged1 = normalize(averaged.copy())

    plt.bar(pd_cases1.index, pd_cases1['confirm'], color='lightgreen', label='daily cases')
    plt.plot(averaged1.index, averaged1['confirm'], color='darkred', label='cases average')


    fig.legend(loc=(legend_pos))
    plt.savefig(os_path.join(out_dir, filename + '_log.png'))
    plt.show()
    plt.close("all")


def generate_plots_R(pd_cases, filename):
    plt.close("all")
    pd_cases.plot(figsize=(20,8),linewidth=2)#subplots=True,
    plt.savefig(os_path.join(out_dir, filename + '.png'))
    plt.show()

#if __name__ == "__main__":
    # cases ='20211212-20230422'
    # deaths_csv = '2023-04-15_deaths.csv'
    # deaths1 = pd.read_csv(filepath_or_buffer=out_dir + deaths_csv, index_col='date', parse_dates=True)
    # deaths = deaths1[pd.to_datetime('20211212') : pd.to_datetime('20230420')]

    # plots_and_deaths_log_and_norm(
    #     pd.read_csv(filepath_or_buffer=out_dir + cases + '.csv', index_col='date', parse_dates=True),
    #     pd.read_csv(filepath_or_buffer=out_dir + cases + '_avg.csv', index_col='date', parse_dates=True),
    #     deaths,
    #     '220423_last'
    #     )
