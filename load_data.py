import polars as pl
from pathlib import Path
from dash import html

# generate HTML table from polars DataFrame
def html_table(dataframe):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col.replace('_',' ').title()) 
                     for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe[col][i] if type(dataframe[col][i])!=float else\
                        round(dataframe[col][i],2)) for col in dataframe.columns
            ]) for i in range(dataframe.shape[0])
        ])
    ])

# team colors for plotting
def teamcolor_data():
    teamcolors = pl.read_parquet(Path('data', 'teamcolors.parquet'))
    teamcolors = teamcolors.select(pl.col(['team','color','color2']))   
    return teamcolors


def passing_data():
    # NGS data, select week 0 for season averages
    passing_data = pl.read_parquet(Path('data', 'ngs_2023_passing.parquet')) 
    
    # season avg, renames, drops
    passing_data = passing_data.filter(pl.col('week')==0)
    passing_data = passing_data.rename({
                    'player_display_name':'player', 'team_abbr':'team', 
                    'expected_completion_percentage':'cp_expected',
                    'completion_percentage_above_expectation':'cp_over_expected'
                                        })
    passing_data = passing_data.drop([
        'season','season_type','week','player_position','player_gsis_id',
        'player_first_name','player_last_name','player_jersey_number',
        'player_short_name','max_completed_air_distance','max_air_distance',
])
    
    # unique check
    if passing_data.shape[0] != passing_data['player'].unique().shape[0]:
        print('QB with more than one occurence, may cause errors.')    
        
    # size cutoff if needed
    stat_dist = passing_data['attempts'].describe()
    cutoff_max = int(stat_dist.filter(pl.col('statistic')=='50%')\
                     ['value'].item())
    
    if passing_data.shape[0] > 40:
        cutoff_min = int(stat_dist.filter(pl.col('statistic')=='25%')\
                         ['value'].item())
    else:
        cutoff_min = 0
        
    # add PFR data, pressures, sacks, ?? dropbacks (calculated) ??
    pfr_data = pl.read_parquet(Path('data', 'advstats_week_pass_2023.parquet'))
    pfr_data = pfr_data.rename({'pfr_player_name':'player'})
    
    # infer dropbacks from pressures, pressure %. Not useful with 0 pressures
    # pfr_data = pfr_data.with_columns(
    #     (pl.col('times_pressured')/pl.col('times_pressured_pct'))
    #     .cast(pl.Int64, strict=False).alias('dropbacks'))
    
    # sum over season
    pfr_data = pfr_data.group_by(['player','team']).agg(
        pl.col(['times_sacked','times_pressured',]).sum())
    # add to NGS dataframe
    passing_data = passing_data.join(pfr_data, on=["player","team"], 
                                     how='left')
        
    return passing_data.fill_null(0), (cutoff_min, cutoff_max)


def rushing_data():
    # NGS data, select week 0 for season averages
    rushing_data = pl.read_parquet(Path('data', 'ngs_2023_rushing.parquet'))  
    
    # season avg, renames, drops
    rushing_data = rushing_data.filter(pl.col('week')==0)
    rushing_data = rushing_data.rename({
        'player_display_name':'player', 'team_abbr':'team', 
        'rush_attempts':'attempts', 
        'expected_rush_yards':'expected_yds',
        'rush_yards_over_expected':'yds_over_expected',
        'rush_yards_over_expected_per_att':'avg_yds_over_expected',
        'percent_attempts_gte_eight_defenders':'percent_eight_defenders',
})
    rushing_data = rushing_data.drop([
        'season','season_type','week','player_position','player_gsis_id',
        'player_first_name','player_last_name','player_jersey_number',
        'player_short_name',
])
    
    # unique check
    if rushing_data.shape[0] != rushing_data['player'].unique().shape[0]:
        print('RB with more than one occurence, may cause errors.')    
        
    # size cutoff if needed
    stat_dist = rushing_data['attempts'].describe()
    cutoff_max = int(stat_dist.filter(pl.col('statistic')=='75%')\
                     ['value'].item())
    
    if rushing_data.shape[0] > 48:
        cutoff_min = int(stat_dist.filter(pl.col('statistic')=='25%')\
                         ['value'].item())
    else:
        cutoff_min = 0
        
    # add PFR data, yds before/after contact, broken tackles
    pfr_data = pl.read_parquet(Path('data', 'advstats_week_rush_2023.parquet'))
    pfr_data = pfr_data.rename({'pfr_player_name':'player',
                        'rushing_yards_before_contact':'yds_before_contact',
                        'rushing_yards_after_contact':'yds_after_contact',
                        'rushing_broken_tackles':'broken_tackles',
                                })
    # sum over season
    pfr_data = pfr_data.group_by(['player','team']).agg(pl.col([
        'yds_before_contact','yds_after_contact','broken_tackles']).sum())
    # add to NGS dataframe
    rushing_data = rushing_data.join(pfr_data, on=["player","team"], 
                                     how='left')
    
    # yds before/after contact and broken tackles to avg per attempt
    rushing_data = rushing_data.with_columns([
(pl.col('yds_before_contact')/pl.col('attempts')).alias('avg_yds_before_contact'),
(pl.col('yds_after_contact')/pl.col('attempts')).alias('avg_yds_after_contact'),
(pl.col('broken_tackles')/pl.col('attempts')).alias('broken_tackles_per_att'),
                                             ])
    rushing_data = rushing_data.drop(['yds_before_contact', 'yds_after_contact',
                                      'broken_tackles'])

    return rushing_data.fill_null(0), (cutoff_min, cutoff_max)

def receiving_data():
    # NGS data, select week 0 for season averages
    receiving_data = pl.read_parquet(Path('data', 'ngs_2023_receiving.parquet'))
    
    # season avg, renames, drops
    receiving_data = receiving_data.filter(pl.col('week')==0)
    receiving_data = receiving_data.rename({
            'player_display_name':'player', 'team_abbr':'team',
            'percent_share_of_intended_air_yards':'share_intended_air_yards',
                                            })
    receiving_data = receiving_data.drop([
        'season','season_type','week','player_position','player_gsis_id',
        'player_first_name','player_last_name','player_jersey_number',
        'player_short_name',
])
    
    # unique check
    if receiving_data.shape[0] != receiving_data['player'].unique().shape[0]:
        print('WR with more than one occurence, may cause errors.')  
        
    # size cutoff if needed
    stat_dist = receiving_data['targets'].describe()
    cutoff_max = int(stat_dist.filter(pl.col('statistic')=='75%')\
                     ['value'].item())
    
    if receiving_data.shape[0] > 64:
        cutoff_min = int(stat_dist.filter(pl.col('statistic')=='50%')\
                         ['value'].item())
    else:
        cutoff_min = 0
        
    # add PFR data, drops, broken tackles
    pfr_data = pl.read_parquet(Path('data', 'advstats_week_rec_2023.parquet'))
    pfr_data = pfr_data.rename({'pfr_player_name':'player',
                                'receiving_drop':'drops',
                                'receiving_broken_tackles':'broken_tackles',})
    # sum over season
    pfr_data = pfr_data.group_by(['player','team']).agg(pl.col([
        'drops','broken_tackles']).sum())    
    # add to NGS dataframe
    receiving_data = receiving_data.join(pfr_data, on=["player","team"], 
                                     how='left')
    # drops to drop %, broken tackles to per rec
    receiving_data = receiving_data.with_columns([
(100*pl.col('drops')/pl.col('targets')).alias('drop_percentage'),
(pl.col('broken_tackles')/pl.col('receptions')).alias('broken_tackles_per_rec'),
                                                 ])
    receiving_data = receiving_data.drop(['drops', 'broken_tackles'])
    
    
    return receiving_data.fill_null(0), (cutoff_min, cutoff_max)
    
    

