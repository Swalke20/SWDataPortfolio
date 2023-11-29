#Takes in dataframes and parameters and returns train, test and validation set X and Y as dataframes.
#Returns a smaller sample if sample and proportion are given

def data_format(train_df, test_df, val_df, sample, proportion):
    train_df = train_df.drop(['Unnamed: 0'], axis=1)
    test_df = test_df.drop(['Unnamed: 0'], axis=1)
    val_df = val_df.drop(['Unnamed: 0'], axis=1)

    train_rows = train_df.shape[1]
    test_rows = test_df.shape[1]
    val_rows = val_df.shape[1]

    if sample!=None:
        train_df = train_df.sample(n=train_rows//proportion, replace=False, random_state=7, axis=0)
        test_df = test_df.sample(n=test_rows//proportion, replace=False, random_state=7, axis=0)
        val_df = val_df.sample(n=val_rows//proportion, replace=False, random_state=7, axis=0)

    X_train = train_df.drop('Winner_num',axis=1)
    y_train = train_df['Winner_num']

    X_test= test_df.drop('Winner_num',axis=1) 
    y_test = test_df['Winner_num']

    X_val= val_df.drop('Winner_num',axis=1) 
    y_val = val_df['Winner_num']
    return(X_train, X_test, X_val, y_train, y_test, y_val)