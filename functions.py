#import required packages
#import nest_asyncio
#nest_asyncio.apply()
import re
from collections import Counter
import chess
from datetime import datetime,timedelta
import chess
from chessdotcom import get_leaderboards, get_player_stats, get_player_game_archives
import requests
import numpy as np
import pandas as pd


def pgn(game,timestamps=False,output='text'):
  """
  Takes game PGN data from chess.com and cleans
  and stores the data based on the arguments below:
  ---------------------------------------------------------------------------------------------------
    - timestamps: the user can opt to include/exclude
      timestamps (timestamps are excluded by default)
    - output: the user can opt to output the data
      as text or dictionary (text is set to default)
  """
  # isolate the move data from the pgn
  pgn_data = game['pgn'].split('\n')[-2]

  if output == 'text':
    if timestamps == False:
      pgn = re.sub("\d+\.\.\.","",re.sub("\{.*?\}","",pgn_data)).replace('   ',' ').replace('  ',' ')
    else:
      pgn = pgn_data

  if output == 'dictionary':
    temp_list = []
    for i in re.sub("\d+\.\.\.","",pgn_data).replace('{',',{').replace('}','},').split(',')[:-1]:
      for j in i.split('. '):
        temp_list.append(j.strip())


    # index the temporary list to seperate each players moves
    move_number = temp_list[0::5]
    white_move = temp_list[1::5]
    black_move = temp_list[3::5]
    white_timestamp = temp_list[2::5]
    black_timestamp = temp_list[4::5]
    white_timestamp_cl = []
    black_timestamp_cl = []


    # if white wins black will have one less move. Append a blank value to blacks lists to make sure
    # arrays are of same length
    if len(white_move) != len(black_move):
      black_move.append('')
      black_timestamp.append('')

    for i in range(len(move_number)):
      if len(white_timestamp[i]) < 18:
        white_timestamp_cl.append(white_timestamp[i].replace('{[%clk ','').replace(']}','') + '.0')
      else:
        white_timestamp_cl.append(white_timestamp[i].replace('{[%clk ','').replace(']}',''))

      if black_timestamp[i] != '':
        if len(black_timestamp[i]) < 18:
          black_timestamp_cl.append(black_timestamp[i].replace('{[%clk ','').replace(']}','')+'.0')
        else:
          black_timestamp_cl.append(black_timestamp[i].replace('{[%clk ','').replace(']}',''))
      else:
        black_timestamp_cl.append(black_timestamp_cl[-1])



    if timestamps == False:
      pgn = {'MoveNumber': move_number, 'WhiteMove': white_move, 'BlackMove': black_move}
    else:
      pgn = {'MoveNumber': move_number, 'WhiteMove': white_move, 'WhiteTimestamp' : white_timestamp_cl, 'BlackMove': black_move, 'BlackTimestamp':black_timestamp_cl}

  return pgn


def eval_points(board):
  """
  A function thath takes a chess board item as an agrument
  and returns a point difference between white and black at a given turn
  """
  #specify the point values for white and blacks pieces
  point_dict_black = {'r': 5,'n':3,'b':3,'q':9,'k':0,'p':1,'.':0}
  point_dict_white = {'R': 5,'N':3,'B':3,'Q':9,'K':0,'P':1,'.':0}

  #initialise counters to sum the points up each players remaining pieces
  black_counter = 0
  white_counter = 0

  #iterate through each position on the board and count point totals
  for i in re.split(' |\n',str(board)):
    if i not in point_dict_black.keys():
      white_counter += point_dict_white[i]
    else:
      black_counter += point_dict_black[i]

  eval_dict = dict(Counter(re.split(' |\n',str(board))))
  del eval_dict['.']
  point_difference  = white_counter - black_counter

  return point_difference, eval_dict


def get_game_data(game):
  """
  Outputs a dictionary with point and time
  difference at each move from PGN data
  """
  #initialise board
  board = chess.Board()

  #output pgn data to dictionary
  game_data = pgn(game,timestamps=True,output='dictionary')

  #iterate through each move and play them on the chess board object
  for i in range(len(game_data['MoveNumber'])):
    board.push_san(game_data['WhiteMove'][i])
    if game_data['BlackMove'][i] != '':
      board.push_san(game_data['BlackMove'][i])

    #after each player has made their move for the turn evaluate the difference in point total
    if 'PointDifference' not in game_data.keys():
      game_data['PointDifference'] = list()
    game_data['PointDifference'].extend([eval_points(board)[0]])

    # evaluate the difference in time remaining for white and black
    if 'TimeDifference' not in game_data.keys():
      game_data['TimeDifference'] = list()
    game_data['TimeDifference'].extend([(datetime.strptime(game_data['WhiteTimestamp'][i],'%H:%M:%S.%f') - datetime.strptime(game_data['BlackTimestamp'][i],'%H:%M:%S.%f')).total_seconds()])

    # dictionary of pieces remiaining
    if 'PiecesRemaining' not in game_data.keys():
      game_data['PiecesRemaining'] = list()
    game_data['PiecesRemaining'].extend([eval_points(board)[1]])



  return game_data


def castle_id(game):
  """
  A function that identifies how and if
  each player castled (short, long or no castle)
  """
  castle_dict = {}
  colours = ['White','Black']
  game_data = get_game_data(game)
  for colour in colours:
    castle = 0
    for i in game_data[str(colour)+'Move']:
      if i == 'O-O':
        castle = 'ShortCastle'
      elif i == 'O-O-O':
        castle = 'LongCastle'

    if castle == 0:
      castle_dict[colour+'Castle'] = 'NoCastle'
    else:
      castle_dict[colour+'Castle'] = castle

  return castle_dict


def game_sum(game):
  """
  A function that returns game data for prespecified move intervals
  """
  move_intervals = [10, 15, 20, 25, 30, 40]
  summary_dict = {}
  piece_names = {'r':'BRook','k':'BKing','b':'BBishop','n':'BKnight','q':'BQueen','p':'BPawn','R':'WRook','K':'WKing','B':'WBishop','N':'WKnight','Q':'WQueen','P':'WPawn'}
  game_data = get_game_data(game)
  for i in move_intervals:
    if len(game_data['MoveNumber'])-1 >= i:
      summary_dict['PointDifference'+str(i)] = game_data['PointDifference'][i-1]
      summary_dict['TimeDifference'+str(i)] = game_data['TimeDifference'][i-1]
      summary_dict['AvgPointDifferenceMove'+str(i)] = sum(game_data['PointDifference'][0:i-1])/len(game_data['PointDifference'][0:i-1])
      summary_dict['AvgTimeDifferenceMove'+str(i)] = sum(game_data['TimeDifference'][0:i-1])/len(game_data['TimeDifference'][0:i-1])

      for j in piece_names.keys():
        if j in game_data['PiecesRemaining'][i-1].keys():
          summary_dict[piece_names[j] + 'Remaining' + str(i)] = game_data['PiecesRemaining'][i-1][j]
        else:
          summary_dict[piece_names[j] + 'Remaining' + str(i)] = 0

    else:
      summary_dict['PointDifference'+str(i)] = np.nan
      summary_dict['TimeDifference'+str(i)] = np.nan
      summary_dict['AvgPointDifferenceMove'+str(i)] = np.nan
      summary_dict['AvgTimeDifferenceMove'+str(i)] = np.nan

      for j in piece_names.keys():
        summary_dict[piece_names[j] + 'Remaining' + str(i)] = np.nan


  if len(game_data['MoveNumber']) != 0:
    summary_dict['AvgPointDifferenceFullGame'] = sum(game_data['PointDifference'])/len(game_data['PointDifference'])
    summary_dict['AvgTimeDifferenceFullGame'] = sum(game_data['TimeDifference'])/len(game_data['TimeDifference'])
    summary_dict['WhiteCastle'] = castle_id(game)['WhiteCastle']
    summary_dict['BlackCastle'] = castle_id(game)['BlackCastle']

  else:
    summary_dict['AvgPointDifferenceFullGame'] = np.nan
    summary_dict['AvgTimeDifferenceFullGame'] = np.nan
    summary_dict['WhiteCastle'] = np.nan
    summary_dict['BlackCastle'] = np.nan

  return summary_dict


def square_check(board,square,print_board=False):
  """
  A function that takes a chess board and a square
  at a given move and returns what piece is on that square
  """
  board_dict = {}
  counter = 0
  clean_board = re.split(' |\n',str(board)[::-1])
  for i in range(0,8):
    board_dict[chr(104-counter)] = clean_board[0+i::8]
    counter+=1
  if print_board == True:
    print(board,'\n')

  return board_dict[square[0]][int(square[-1])-1]


def game_results(time_control='900+10',colour=0):
  if colour == 0:
    consol_df = pd.pivot_table(full_game_data[((full_game_data['Last'+str(7)+'Days'] == 1) & (full_game_data['TimeControl'] == time_control))],
                      index='TimeControl',values=['Win','Loss','Draw'])

    for i in [14,30,90,180,365]:
      temp_df = pd.pivot_table(full_game_data[((full_game_data['Last'+str(i)+'Days'] == 1) & (full_game_data['TimeControl'] == time_control))],
                  index='TimeControl',values=['Win','Loss','Draw'])
      consol_df =  consol_df.append(temp_df,ignore_index=True)

    consol_df['Number of Days'] = ['Last 7 Days','Last 14 Days','Last 30 Days','Last 90 Days','Last 180 Days','Last 365 Days']
    consol_df = consol_df[['Number of Days','Win','Loss','Draw']].set_index('Number of Days')
    consol_df.plot(kind='barh', stacked=True,color=['g','r','grey'],title='Game History for White and Black at ' + str(time_control) + ' Time Control')
    consol_df.plot(kind='area',color=['g','r','grey'],title='Game History for White and Black at ' + str(time_control) + ' Time Control')
  else:
    consol_df = pd.pivot_table(full_game_data[((full_game_data['Last'+str(7)+'Days'] == 1) & (full_game_data['TimeControl'] == time_control) & (full_game_data['Colour'] == colour))],
                      index='TimeControl',values=['Win','Loss','Draw'])

    for i in [14,30,90,180,365]:
      temp_df = pd.pivot_table(full_game_data[((full_game_data['Last'+str(i)+'Days'] == 1) & (full_game_data['TimeControl'] == time_control) & (full_game_data['Colour'] == colour))],
                  index='TimeControl',values=['Win','Loss','Draw'])
      consol_df =  consol_df.append(temp_df,ignore_index=True)

    consol_df['Number of Days'] = ['Last 7 Days','Last 14 Days','Last 30 Days','Last 90 Days','Last 180 Days','Last 365 Days']
    consol_df = consol_df[['Number of Days','Win','Loss','Draw']].set_index('Number of Days')
    consol_df.plot(kind='barh', stacked=True,color=['g','r','grey'],title='Game History for ' + str(colour) + ' at ' + str(time_control) + ' Time Control')
    consol_df.plot(kind='area',color=['g','r','grey'],title='Game History for ' +str(colour) + ' at ' + str(time_control) + ' Time Control')
  return consol_df.round(3)


def full_game_data(player_name):
  """
  Returns comprehensive game data for the specified user
  """

  game_dict = {}
  counter=0

  # iterate through the urls for games during each month of the year
  for url in get_player_game_archives(player_name).json['archives']:
    # through each url iterate through all of the games in that given month
    for game in requests.get(url).json()['games']:
      text_split = game['pgn'].split('\n')
      counter+=1
      # from each PGN strip the details of each game and place into a dictionary
      for i in text_split[:-3]:
        split_text = i.strip('[]').replace('"','').split(' ')
        key = split_text[0]
        value = ' '.join(split_text[1:])
        if key not in game_dict:
          game_dict[key] = list()
        game_dict[key].extend([value])

      # add moves from the pgn to dictionary
      if 'pgn' not in game_dict:
        game_dict['pgn'] = list()
      game_dict['pgn'].extend([pgn(game,timestamps=True)])

      # add moves from the pgn to dictionary without time stamps
      if 'pgnNoTime' not in game_dict:
        game_dict['pgnNoTime'] = list()
      game_dict['pgnNoTime'].extend([pgn(game,timestamps=False)])


      #time remaining for black and white
      pgn_dict = pgn(game,timestamps=True,output='dictionary') #declare PGN dictionary so function only needs to be called once per game

      if 'BlackTimeRemaining' not in game_dict:
        game_dict['WhiteTimeRemaining'] = list()
        game_dict['BlackTimeRemaining'] = list()


      if len(pgn_dict['WhiteTimestamp']) < 2:
        game_dict['WhiteTimeRemaining'].extend([np.nan])
        game_dict['BlackTimeRemaining'].extend([np.nan])
      else:
        game_dict['WhiteTimeRemaining'].extend([pgn_dict['WhiteTimestamp'][-1]])

        if pgn_dict['BlackTimestamp'][-1] == '':
          game_dict['BlackTimeRemaining'].extend([pgn_dict['BlackTimestamp'][-2]])
        else:
          game_dict['BlackTimeRemaining'].extend([pgn_dict['BlackTimestamp'][-1]])

      if 'NumberOfMoves' not in game_dict:
        game_dict['NumberOfMoves'] = list()

      if len(pgn_dict['MoveNumber']) < 2:
        game_dict['NumberOfMoves'].extend([np.nan])

      else:
        game_dict['NumberOfMoves'].extend([pgn_dict['MoveNumber'][-1]])

      game_summary = game_sum(game)
      for i in game_summary.keys():
        if i not in game_dict:
          game_dict[i] = list()
        game_dict[i].extend([game_summary[i]])



      for i in game_dict.keys():
        if len(game_dict[i]) < counter:
          game_dict[i].extend([''])

  full_game_data = pd.DataFrame(game_dict)

  #exclude friendly games
  full_game_data = full_game_data[full_game_data['Event'] != "Let's Play!"].reset_index()

  #cast date as datetime
  full_game_data['Date'] = pd.to_datetime(full_game_data['Date'])

  full_game_data['NumberOfMoves'] = full_game_data['NumberOfMoves'].astype('float')

  #change the timezone and calculate the lenth of the game
  full_game_data['ACSTStartDateTime'] = pd.to_datetime(full_game_data['UTCDate']+' '+full_game_data['UTCTime']) + timedelta(hours=9,minutes=30)
  full_game_data['ACSTEndDateTime'] = pd.to_datetime(full_game_data['UTCDate']+' '+full_game_data['EndTime']) + timedelta(hours=9,minutes=30)
  full_game_data['Game Length'] = (full_game_data['ACSTEndDateTime'] - full_game_data['ACSTStartDateTime']).dt.total_seconds()

  # time of day classification (morining, afternoon, evening, night)
  full_game_data['TimeOfDay'] = full_game_data['ACSTStartDateTime'].apply(lambda x: 'morning' if x < x.replace(hour=10, minute=0, second=0, microsecond=0)
                                                                          else ('early afternoon' if x < x.replace(hour=12, minute=0, second=0, microsecond=0)
                                                                          else ('late afternoon' if x < x.replace(hour=17, minute=0, second=0, microsecond=0)
                                                                          else ('evening' if x < x.replace(hour=20, minute=0, second=0, microsecond=0) else 'night'))))

  # weekend classification
  full_game_data['DayOfWeek'] = full_game_data['ACSTStartDateTime'].dt.weekday
  full_game_data['Weekend'] = full_game_data['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)

  # my peices
  full_game_data['Colour'] = full_game_data['White'].apply(lambda x: 'white' if x =='VincentHK99' else 'black')

  # your Elo column
  full_game_data.loc[full_game_data['Colour'] == 'white','Elo'] = full_game_data['WhiteElo']
  full_game_data.loc[full_game_data['Colour'] == 'black','Elo'] = full_game_data['BlackElo']


  # opponents elo column
  full_game_data.loc[full_game_data['Colour'] == 'white','OppElo'] = full_game_data['BlackElo']
  full_game_data.loc[full_game_data['Colour'] == 'black','OppElo'] = full_game_data['WhiteElo']

  # GameResult
  full_game_data.loc[((full_game_data['Result'] == '1-0') & (full_game_data['Colour'] == 'white')),'Win'] = 1
  full_game_data.loc[((full_game_data['Result'] == '0-1') & (full_game_data['Colour'] == 'black')),'Win'] = 1
  full_game_data.loc[((full_game_data['Result'] == '1-0') & (full_game_data['Colour'] == 'black')),'Win'] = 0
  full_game_data.loc[((full_game_data['Result'] == '0-1') & (full_game_data['Colour'] == 'white')),'Win'] = 0
  full_game_data.loc[full_game_data['Result'] == '1/2-1/2','Win'] = 0

  full_game_data.loc[((full_game_data['Result'] == '1-0') & (full_game_data['Colour'] == 'white')),'Loss'] = 0
  full_game_data.loc[((full_game_data['Result'] == '0-1') & (full_game_data['Colour'] == 'black')),'Loss'] = 0
  full_game_data.loc[((full_game_data['Result'] == '1-0') & (full_game_data['Colour'] == 'black')),'Loss'] = 1
  full_game_data.loc[((full_game_data['Result'] == '0-1') & (full_game_data['Colour'] == 'white')),'Loss'] = 1
  full_game_data.loc[full_game_data['Result'] == '1/2-1/2','Loss'] = 0

  full_game_data.loc[full_game_data['Result'] == '1/2-1/2','Draw'] = 1
  full_game_data.loc[full_game_data['Result'] != '1/2-1/2','Draw'] = 0


  # last 7, 14, 30, 90, 180 days
  full_game_data['Last7Days'] = (datetime.now() - full_game_data['ACSTEndDateTime']).dt.days.apply(lambda x: 1 if x <= 7 else 0)
  full_game_data['Last14Days'] = (datetime.now() - full_game_data['ACSTEndDateTime']).dt.days.apply(lambda x: 1 if x <= 14 else 0)
  full_game_data['Last30Days'] = (datetime.now() - full_game_data['ACSTEndDateTime']).dt.days.apply(lambda x: 1 if x <= 30 else 0)
  full_game_data['Last90Days'] = (datetime.now() - full_game_data['ACSTEndDateTime']).dt.days.apply(lambda x: 1 if x <= 90 else 0)
  full_game_data['Last180Days'] = (datetime.now() - full_game_data['ACSTEndDateTime']).dt.days.apply(lambda x: 1 if x <= 180 else 0)
  full_game_data['Last365Days'] = (datetime.now() - full_game_data['ACSTEndDateTime']).dt.days.apply(lambda x: 1 if x <= 365 else 0)
  full_game_data['Over365Days'] = (datetime.now() - full_game_data['ACSTEndDateTime']).dt.days.apply(lambda x: 1 if x > 365 else 0)










  #seconds of time remaining
  full_game_data['WhiteTimeRemaining'] = (pd.to_datetime(full_game_data['WhiteTimeRemaining']) - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).dt.total_seconds()
  full_game_data['BlackTimeRemaining'] = (pd.to_datetime(full_game_data['BlackTimeRemaining']) - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).dt.total_seconds()


  #my time remaining and opp time remaining
  full_game_data.loc[full_game_data['Colour'] == 'white','MyTimeRemaining'] = full_game_data['WhiteTimeRemaining']
  full_game_data.loc[full_game_data['Colour'] == 'black','MyTimeRemaining'] = full_game_data['BlackTimeRemaining']

  full_game_data.loc[full_game_data['Colour'] == 'white','OppTimeRemaining'] = full_game_data['BlackTimeRemaining']
  full_game_data.loc[full_game_data['Colour'] == 'black','OppTimeRemaining'] = full_game_data['WhiteTimeRemaining']

  #time diff vs opponent
  full_game_data['+/-TimeDifference'] = full_game_data['MyTimeRemaining'] - full_game_data['OppTimeRemaining']

  #total time
  full_game_data.loc[full_game_data['TimeControl'].str.contains('\+') == 1,'TotalTime'] = full_game_data['TimeControl'].str.replace('^.*?(?=\+)','').astype('int') * full_game_data['NumberOfMoves'] + full_game_data['TimeControl'].str[0:3].astype('int')
  full_game_data.loc[full_game_data['TimeControl'].str.contains('\+') == 0,'TotalTime'] = full_game_data['TimeControl']
  full_game_data['TotalTime'] = full_game_data['TotalTime'].astype('float')

  # my time per move
  full_game_data['MyTimeUsed'] = full_game_data['TotalTime'] - full_game_data['MyTimeRemaining']
  full_game_data['AvgTimePerMove'] = full_game_data['MyTimeUsed'] / full_game_data['NumberOfMoves']

  # opponents time per move
  full_game_data['OppTimeUsed'] = full_game_data['TotalTime'] - full_game_data['OppTimeRemaining']
  full_game_data['OppAvgTimePerMove'] = full_game_data['OppTimeUsed'] / full_game_data['NumberOfMoves']

  # +/- time per move difference
  full_game_data['+/-AvgTimePerMove'] = full_game_data['AvgTimePerMove'] - full_game_data['OppAvgTimePerMove']

  # games in session
  full_game_data['SessionGame'] = (full_game_data['ACSTStartDateTime'].shift(-1)-full_game_data['ACSTEndDateTime']).dt.total_seconds().apply(lambda x: 1 if x < 6000 else 0)

  game_in_session =[]
  counter=0
  for i in full_game_data['SessionGame'].tolist():
    if counter == 0:
      game_in_session.append(i)

    else:
      if i == 0:
        game_in_session.append(i)
      else:
        game_in_session.append(i + game_in_session[i-2])

    counter +=1

  full_game_data['GameInSession'] = game_in_session


  # openings title (WIP)

  # termination further mapping
  term_list = ['stalemate', 'insufficient material','timeout vs insufficient material','agreement',
              'repetition','resignation','checkmate','game abandoned','on time']
  for i in term_list:
    full_game_data.loc[full_game_data['Termination'].str.contains(i,case=False),'ReasonedTerminated'] = i


  return full_game_data


def game_results(game_data,time_control='900+10',colour=0):
  """
  Returns Win/Draw/Loss percentages for games over different timen horizons (7,14,30,90 days ect.)
  """
  if colour == 0:
    consol_df = pd.pivot_table(game_data[((game_data['Last'+str(7)+'Days'] == 1) & (game_data['TimeControl'] == time_control))],
                      index='TimeControl',values=['Win','Loss','Draw'])

    for i in [14,30,90,180,365]:
      temp_df = pd.pivot_table(game_data[((game_data['Last'+str(i)+'Days'] == 1) & (game_data['TimeControl'] == time_control))],
                  index='TimeControl',values=['Win','Loss','Draw'])
      consol_df =  consol_df.append(temp_df,ignore_index=True) 

    consol_df['Number of Days'] = ['Last 7 Days','Last 14 Days','Last 30 Days','Last 90 Days','Last 180 Days','Last 365 Days']
    consol_df = consol_df[['Number of Days','Win','Loss','Draw']].set_index('Number of Days')
  else:
    consol_df = pd.pivot_table(game_data[((game_data['Last'+str(7)+'Days'] == 1) & (game_data['TimeControl'] == time_control) & (game_data['Colour'] == colour))],
                      index='TimeControl',values=['Win','Loss','Draw'])

    for i in [14,30,90,180,365]:
      temp_df = pd.pivot_table(game_data[((game_data['Last'+str(i)+'Days'] == 1) & (game_data['TimeControl'] == time_control) & (game_data['Colour'] == colour))],
                  index='TimeControl',values=['Win','Loss','Draw'])
      consol_df =  consol_df.append(temp_df,ignore_index=True) 

    consol_df['Number of Days'] = ['Last 7 Days','Last 14 Days','Last 30 Days','Last 90 Days','Last 180 Days','Last 365 Days']
    consol_df = consol_df[['Number of Days','Win','Loss','Draw']].set_index('Number of Days')
  return consol_df.round(3)


def opening_sum_eco(game_data,opening_class,days_analysed=0):
  if days_analysed !=0:
    game_data = game_data[game_data['Last'+str(days_analysed)+'Days'] == 1]
  eco_sum = pd.pivot_table(game_data,index=['higherMapping','name','ecoCode'],values=['Win','Loss','Draw','PointDifference10','PointDifference20','PointDifference30','PointDifference40','Event'],
                           aggfunc={'Win': np.mean, 'Draw': np.mean,'Loss': np.mean,'PointDifference10':np.mean,'PointDifference20':np.mean,
                                    'PointDifference30':np.mean,'PointDifference40':np.mean,'Event':np.count_nonzero})
  
  return eco_sum[['Win','Loss','Draw','PointDifference10','PointDifference20','PointDifference30','PointDifference40','Event']].loc[opening_class].round(3)


def opening_sum_subclass(game_data,opening_class,days_analysed=0,):
  if days_analysed !=0:
    game_data = game_data[game_data['Last'+str(days_analysed)+'Days'] == 1]
  eco_sum = pd.pivot_table(game_data,index=['higherMapping','name'],values=['Win','Loss','Draw','PointDifference10','PointDifference20','PointDifference30','PointDifference40','Event'],
                           aggfunc={'Win': np.mean, 'Draw': np.mean,'Loss': np.mean,'PointDifference10':np.mean,'PointDifference20':np.mean,
                                    'PointDifference30':np.mean,'PointDifference40':np.mean,'Event':np.count_nonzero})
  
  return eco_sum[['Win','Loss','Draw','PointDifference10','PointDifference20','PointDifference30','PointDifference40','Event']].loc[opening_class].round(3)


def opening_sum_class(game_data,days_analysed=0):
  if days_analysed !=0:
    game_data = game_data[game_data['Last'+str(days_analysed)+'Days'] == 1]
  eco_sum = pd.pivot_table(game_data,index='higherMapping',values=['Win','Loss','Draw','PointDifference10','PointDifference20','PointDifference30','PointDifference40','Event'],
                           aggfunc={'Win': np.mean, 'Draw': np.mean,'Loss': np.mean,'PointDifference10':np.mean,'PointDifference20':np.mean,
                                    'PointDifference30':np.mean,'PointDifference40':np.mean,'Event':np.count_nonzero})
  
  return eco_sum[['Win','Loss','Draw','PointDifference10','PointDifference20','PointDifference30','PointDifference40','Event']].round(3)


def data_clean(game_data):
  """
  Makes sure the timedifference, point difference and piece remaining values in the dataframe are from the 
  perspective of the player who's username is entered rather than whoever is white
  """
  pt_columns = ['PointDifference10','TimeDifference10','AvgPointDifferenceMove10','AvgTimeDifferenceMove10','PointDifference15','TimeDifference15',
           'AvgPointDifferenceMove15','AvgTimeDifferenceMove15','PointDifference20','TimeDifference20','AvgPointDifferenceMove20','AvgTimeDifferenceMove20',
           'PointDifference25','TimeDifference25','AvgPointDifferenceMove25','AvgTimeDifferenceMove25','PointDifference30','TimeDifference30',
           'AvgPointDifferenceMove30','AvgTimeDifferenceMove30','PointDifference40','TimeDifference40','AvgPointDifferenceMove40','AvgTimeDifferenceMove40',
           'AvgPointDifferenceFullGame','AvgTimeDifferenceFullGame']

  wcolumns = ['WBishopRemaining10',	'WBishopRemaining15',	'WBishopRemaining20',	'WBishopRemaining25',	'WBishopRemaining30',
            'WBishopRemaining40',	'WKingRemaining10',	'WKingRemaining15',	'WKingRemaining20',	'WKingRemaining25',	'WKingRemaining30',
            'WKingRemaining40',	'WKnightRemaining10',	'WKnightRemaining15',	'WKnightRemaining20',	'WKnightRemaining25',	'WKnightRemaining30',	
            'WKnightRemaining40',	'WPawnRemaining10',	'WPawnRemaining15',	'WPawnRemaining20',	'WPawnRemaining25',	'WPawnRemaining30',	'WPawnRemaining40',	
            'WQueenRemaining10',	'WQueenRemaining15',	'WQueenRemaining20',	'WQueenRemaining25',	'WQueenRemaining30',	'WQueenRemaining40',	'WRookRemaining10',	
            'WRookRemaining15',	'WRookRemaining20',	'WRookRemaining25',	'WRookRemaining30','WRookRemaining40']

  bcolumns = ['BBishopRemaining10',	'BBishopRemaining15',	'BBishopRemaining20',	'BBishopRemaining25',	'BBishopRemaining30',	'BBishopRemaining40',
            'BKingRemaining10',	'BKingRemaining15',	'BKingRemaining20',	'BKingRemaining25',	'BKingRemaining30',	'BKingRemaining40',	'BKnightRemaining10',
            'BKnightRemaining15',	'BKnightRemaining20',	'BKnightRemaining25',	'BKnightRemaining30',	'BKnightRemaining40',	'BPawnRemaining10',	'BPawnRemaining15',
            'BPawnRemaining20',	'BPawnRemaining25',	'BPawnRemaining30',	'BPawnRemaining40',	'BQueenRemaining10',	'BQueenRemaining15',	'BQueenRemaining20',
            'BQueenRemaining25',	'BQueenRemaining30',	'BQueenRemaining40',	'BRookRemaining10',	'BRookRemaining15',	'BRookRemaining20',	'BRookRemaining25',
            'BRookRemaining30',	'BRookRemaining40']


  for column in pt_columns:
    game_data[column][game_data['Colour'] == 'black'] =  game_data[column] * -1

  for i in range(len(wcolumns)):
    game_data.loc[game_data['Colour'] == 'white', 'My' + wcolumns[i][1:]] = game_data[wcolumns[i]]
    game_data.loc[game_data['Colour'] == 'black', 'My' + wcolumns[i][1:]] = game_data[bcolumns[i]]
    game_data.loc[game_data['Colour'] == 'white', 'Opp' + wcolumns[i][1:]] = game_data[bcolumns[i]]
    game_data.loc[game_data['Colour'] == 'black', 'Opp' + wcolumns[i][1:]] = game_data[wcolumns[i]]

  return game_data


def middlegame_analysis(game_data,colour=0,days_analysed=0):
  if colour != 0:
    game_data = game_data[game_data['Colour'] == colour]
  if days_analysed !=0:
     game_data = game_data[game_data['Last'+str(days_analysed)+'Days'] == 1]
  middle_sum = pd.pivot_table(game_data,index='PointDifference10Mapping',values=['PointDifference15','PointDifference20','PointDifference30','PointDifference40','Win','Draw','Loss','Event'],
               aggfunc={'PointDifference15':np.mean,'PointDifference20':np.mean,'PointDifference30':np.mean,'PointDifference40':np.mean,'Win':np.mean,'Draw':np.mean,'Loss':np.mean,'Event':np.count_nonzero})
  
  return middle_sum[['PointDifference15','PointDifference20','PointDifference30','PointDifference40','Win','Draw','Loss','Event']].round(3)
