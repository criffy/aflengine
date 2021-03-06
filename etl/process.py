#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 20:30:04 2018

@author: chrisstrods
"""

import pandas as pd
from os.path import dirname, abspath

try:
    import shared_functions as f
except ModuleNotFoundError:
    from etl import shared_functions as f


def main():
    #load files
    d = dirname(dirname(abspath(__file__)))
    
    
    summaries = pd.read_csv(d+"/staging/match_summaries.csv")
    player_stats = pd.read_csv(d+"/staging/player_stats.csv",low_memory=False)
    odds = pd.read_csv(d+"/staging/odds_data.csv")
    fantasy = pd.read_csv(d+"/staging/fantasy_scores.csv")
    adv_stats = pd.read_csv(d+"/staging/adv_stats.csv")
    quarters = pd.read_csv(d+"/staging/q_lengths.csv")
    progression = pd.read_csv(d+"/staging/scoring_progression.csv")
    
    
    #Drop any records which have been scraped twice
    summaries.drop_duplicates(inplace=True)
    player_stats.drop_duplicates(inplace=True)
    odds.drop_duplicates(inplace=True)
    fantasy.drop_duplicates(inplace=True)
    adv_stats.drop_duplicates(inplace=True)
    quarters.drop_duplicates(inplace=True)
    progression.drop_duplicates(inplace=True)
    
    
    #######
    #
    # PROCESS PLAYER STATS AND MATCH SUMMARIES
    #
    #######
    
    
    #Generate columns for odds file
    odds["hometeam"] = odds.apply(f.nameFormat, col="hometeam", axis=1)
    odds["awayteam"] = odds.apply(f.nameFormat, col="awayteam", axis=1)
    odds["year"] = odds.apply(f.getYear, axis=1)
    odds["round"] = odds.apply(f.fixFinalsRounds,axis=1)
    odds["matchid"] = odds.apply(f.getMatchID, axis=1)
    
    
    #Summaries update for GF replays
    summaries["matchid"] = summaries.apply(f.replayFix,axis=1)
    summaries["round"] = summaries.apply(f.roundFix,axis=1)
    
    #Merge fantasy with odds to get match details
    fantasy = pd.merge(fantasy,odds,how="left",on="gameID")
    #fantasy.drop(["gameID"], axis=1, inplace=True)
    
    #Generate merge columns to get join key for fantasy file
    fantasy["fullname"] = fantasy.apply(f.nameClean,axis=1)
    fantasy["namekey"] = fantasy.apply(f.getNameKeyFW,axis=1)
    fantasy["fullkey"] = fantasy.apply(f.getFullKey,axis=1)
    
    adv_stats["shortname"] = adv_stats.apply(f.shortName,axis=1)
    fantasy["shortname"] = fantasy.apply(f.shortName,axis=1)
    
    
    fw_data = fantasy.merge(adv_stats,on=["gameID","shortname"],how='inner')
    
    fw_data.drop(["round","date","time","homeodds","homeline","awayodds", \
                  "awayline","hometeam","awayteam","year","homeAway_y","name_y"], \
                  axis=1,inplace=True)
    
    fw_data.rename(columns={'name_x':'name',
                            'homeAway_x':'homeAway'},inplace=True)              
    
    
    
    #Generate merge columns to get join key for player stats file
    
    player_stats["namekey"] = player_stats.apply(f.getNameKeyAT,axis=1)
    player_stats["fullkey"] = player_stats.apply(f.getFullKey,axis=1)
    
    
    #Make manual adjustments for discrepancies
    player_stats["fullkey"] = player_stats.apply(f.fixFullName,axis=1)
    
    
    #Join match summaries with odds file to get all match data
    full_summaries = pd.merge(summaries,odds,how="left",on="matchid")
    
    
    
    #Join player stats with fantasy file and advanced stats file to get all player data
    #player_temp = pd.merge(player_stats,fantasy,how="left",on="fullkey")
    player_full = pd.merge(player_stats,fw_data,how="left",on="fullkey")
       
    #Rename columns in full player file and remove uneeded ones
    player_full.rename(columns={'matchid_x':'matchid', \
                                'kicks_x':'kicks',\
                                'homeAway_x':'homeAway',\
                                'name_x':'name',\
                                'fullname_x':'fullname',\
                                'namekey_x':'namekey'},inplace=True)
    player_full.drop(["namekey_y","matchid_y","kicks_y"], \
                  axis=1,inplace=True)
        
    #Rename columns in match summary file and remove uneeded ones
    full_summaries.rename(columns={'round_x':'round', \
                                'date_x':'date',\
                                'time_x':'time'},inplace=True)
    full_summaries.drop(["round_y","date_y","time_y","hometeam","awayteam",\
                         "year"], \
                  axis=1,inplace=True)
    
    
        
       
    player_full = player_full.reindex(sorted(player_full.columns), axis=1)
        
    
    
    #Turn stat columns into integers
    player_full[['AFLfantasy','centre_clearances','disposal_efficiency',\
                 'effective_disposals','goal_assists','intercepts',\
                 'metres_gained','stoppage_clearances',\
                 'score_involvements','Supercoach',\
                 'tackles_in_50','turnovers',\
                 'behinds','bounces','brownlow',\
                 'clangers','clearances','contested_marks',\
                 'contested_poss','disposals','frees_against',\
                 'frees_for','goal_assists','goals','handballs',\
                 'hitouts','inside50','kicks',\
                 'marks','marks_in_50','number','one_percenters',\
                 'rebound50','tackles','tog','uncontested_poss']]=\
                 player_full[['AFLfantasy','CCL','DE','ED','GA','ITC',\
                              'MG','SCL','SI','Supercoach','T5','TO',\
                              'behinds','bounces','brownlow',\
                              'clangers','clearances','contested_marks',\
                              'contested_poss','disposals','frees_against',\
                              'frees_for','goal_assists','goals','handballs',\
                              'hitouts','inside50','kicks',\
                              'marks','marks_in_50','number','one_percenters',\
                              'rebound50','tackles','tog',\
                              'uncontested_poss']].apply(pd.to_numeric,errors='coerce')            
              
    
    player_full.drop(['BO','CCL','CM','CP','DE','ED','GA','ITC','MG',\
                      'MI5','P1','SCL','SI','T5','TO',\
                      'UP',\
                      'gameID','ha',\
                      'name'],axis=1,inplace=True)
    
                 
    #Drop any duplicate games
    full_summaries.drop_duplicates(subset="matchid",inplace=True)
    player_full.drop_duplicates(subset="fullkey",inplace=True)
    
    
    
    #Convert blank number fields to zeroes
    full_summaries['crowd'] =  full_summaries['crowd'].apply(
        lambda x: 0 if x == "" else x)
    

    
    #Remove trailing spaces on names
    player_full["first_name"] = player_full["first_name"].str.strip()
    full_summaries["umpire1"] = full_summaries["umpire1"].str.strip()
    full_summaries["umpire2"] = full_summaries["umpire2"].str.strip()
    full_summaries["umpire3"] = full_summaries["umpire3"].str.strip()
    
    
    
    #Create final scores and make them ints
    full_summaries["hscore"] = full_summaries.apply(lambda row: row["hteam_q4"].split(".")[2],axis=1)
    full_summaries["ascore"] = full_summaries.apply(lambda row: row["ateam_q4"].split(".")[2],axis=1)
    full_summaries ["hscore"] = pd.to_numeric(full_summaries["hscore"])
    full_summaries ["ascore"] = pd.to_numeric(full_summaries["ascore"])
    
    
    full_summaries['crowd'] = pd.to_numeric(full_summaries['crowd'], errors='coerce').fillna(0)
    
    #Add season column for player stats
    player_full["season"] = player_full.apply(f.fillYear,axis=1)
    
    
    #player_full.to_sparse()
    
    temp_pf = player_full.fillna("0")
    
    
    player_full = temp_pf 
    
    
    
    #######
    #
    # PROCESS SCORING PROGRESSION AND QUARTER LENGTHS
    #
    #######
    quarters["minutes"] = quarters.apply(lambda row: int(row["minutes"].replace("m","")),axis=1)
    quarters["seconds"] = quarters.apply(lambda row: int(row["seconds"].replace("s","")),axis=1)
    
    progression["minutes"] = progression.apply(lambda row: int(row["minutes"]),axis=1)
    progression["seconds"] = progression.apply(lambda row: int(row["seconds"]),axis=1)
    progression["quarter"] = progression.apply(lambda row: int(row["quarter"]),axis=1)
    
    
    
    #Output to CSV
    player_full.to_csv(d+"/bench/players.csv", mode="w", index=False)
    full_summaries.to_csv(d+"/bench/matches.csv", mode="w", index=False)
    progression.to_csv(d+"/bench/progression.csv", mode="w", index=False)
    quarters.to_csv(d+"/bench/quarters.csv", mode="w", index=False)
    

    
#if __name__ == "__main__":
#   main()
