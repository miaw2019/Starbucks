import pandas as pd
from datetime import datetime
from sklearn.preprocessing import MultiLabelBinarizer,OneHotEncoder




def process_portfolio(path):
    """Read and process portfolio data
    
    Arguments:
        path {str} -- the path of portfolio data
    """    
    portfolio_raw = pd.read_json(path, orient='records', lines=True)

    # Fix Column name
    portfolio_raw.rename(columns={"id": "offer_id"},inplace=True)

    # create a dataframe of the 4 individual channel columns
    mlb = MultiLabelBinarizer()
    mlb.fit(portfolio_raw['channels'])
    offer_channels = pd.DataFrame(mlb.transform(portfolio_raw['channels']),
        columns=mlb.classes_)

    # drop the original channels column from `portfolio_raw`
    portfolio = portfolio_raw.drop('channels',axis=1)

    # concatenate the original dataframe with the new `offer_channels` dataframe
    portfolio = pd.concat([portfolio, offer_channels], axis = 1)

    return portfolio

def process_profile(path):
    """Read and process profile data 

    Arguments:
        path {str} -- the path of profile data
    """    
    profile = pd.read_json(path, orient='records', lines=True)

    # Fix Column name
    profile.rename(columns={"id": "customer_id"},inplace=True)

    # Drop custpmers with missing data.
    profile = profile[profile['gender'].notnull()]
    profile = profile[profile['income'].notnull()]
    profile = profile[profile.age != 118]

    # Convert column data type
    profile.became_member_on = pd.to_datetime(profile.became_member_on,format='%Y%m%d')
    profile.replace({'gender': {'F': 0, 'M': 1, 'O': 2}}, inplace=True)
    profile = profile.astype({'gender':'int32'})
    profile = profile[profile['gender']!=2]

    # Add calculated column
    profile['became_member_on_dayofweek'] = profile.became_member_on.dt.dayofweek
    profile['became_member_on_year'] = profile.became_member_on.dt.year
    profile['became_member_on_month'] = profile.became_member_on.dt.month
        
    for i in range(11):
        if i != 0:
            stage = i * 10
            profile[str(stage)+"'s"] = profile['age'].apply(lambda x:1 if((x-stage<10)and (x-stage>=0)) else 0)
    
    return profile

def process_transcript(path):
    """Read and process transcript data
    
    Arguments:
        path {str} -- the path of transcript data
    """    
    transcript = pd.read_json(path, orient='records', lines=True)
    # create a dataframe of the 3 individual value columns
    values_df = pd.DataFrame(transcript.value.tolist())
    values_df['offer id'].fillna(values_df['offer_id'],inplace=True)
    values_df.drop('offer_id', axis=1,inplace=True)
    values_df.rename(columns={"offer id": "offer_id"},inplace=True)

    # concatenate the original dataframe with the new `offer_channels` dataframe
    transcript = pd.concat([transcript, values_df], axis = 1)

    # drop the original channels column from `portfolio`
    transcript = transcript.drop('value',axis=1)

    # change person to customer_id
    transcript.rename(columns={"person": "customer_id"},inplace=True)

    # change hour to day
    transcript['time'] /= 24.0

    # One hot encoding event column
    offer_event =  pd.get_dummies(transcript['event'])
    transcript = pd.concat([transcript, offer_event], axis = 1)
    # transcript = transcript.drop('event',axis=1)
    transcript.rename(columns={"offer received": "received",
                            "offer viewed":"viewed",
                            "offer completed":"completed"
                            },inplace=True)
    offer = transcript[transcript.event.isin(['offer received','offer viewed','offer completed'])][['event','offer_id','customer_id','time','received','viewed','completed']]
    transaction = transcript[transcript.event =='transaction' ][['customer_id','time','amount']]
    return offer,transaction