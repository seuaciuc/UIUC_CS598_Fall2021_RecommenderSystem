import streamlit as st
import pickle
import numpy as np
import pandas as pd
import surprise 


### INPUTS
MINREVIEW = 10
K = 5
pklfile = 'movieRatings.pkl'
ratingsFile = 'ratings.dat'
newuserID = 9999
seed = 42

# load file
fid = open(pklfile,'rb')
movieRatings = pickle.load(fid)
fid.close()


genres = list(movieRatings.columns[3:21])



### FUNCTION TO OBTAIN THE RECOMMENDATIONS
def getGenderBasedRecommendations(movieRatings,genre,K):
    f = movieRatings[movieRatings[genre]==1] 
    byPopularity = f.sort_values(by=['nReviews','avgRating'],ascending=False, ignore_index=True)
    # add filter by number of reviews, sort by average rating
    f2 = f[f['nReviews']>=MINREVIEW] 
    byRating = f2.sort_values(by=['avgRating','nReviews'],ascending=False, ignore_index=True)
    return byPopularity[['Title','avgRating','nReviews']][0:K], byRating[['Title','avgRating','nReviews']][0:K]


# list of 10 most popular movies for review (abstracted from inspection of movieRatings)
top10 = movieRatings.sort_values(by='nReviews',ascending=False,ignore_index=True)[:10]

### CREATE THE SIDE BAR FOR CHOICE OF RECOMMENDER SYSTEM
st.sidebar.title("Recommender Systems")
radio = st.sidebar.radio(label="Choose a system", options=["Genre-based", "Collaborative"])

### SET MODEL
SVD = surprise.SVD(biased=False,reg_all=0.4,random_state=seed)
reader = surprise.Reader(rating_scale=(1,5))


### GENDER-BASED RECOMMENDATIONS
if radio == "Genre-based":
    # allow user choice of genre
    genre = st.selectbox(
    'Please choose a movie genre to obtain recommendations:',
     genres)
    # obtain recommendations
    byPopularity, byRating = getGenderBasedRecommendations(movieRatings,genre,K)
    # re-index to start at 1
    byPopularity.index = range(1,K+1)
    byRating.index = range(1,K+1)
    # change column names
    cols = ['Movie Title','Average Rating','Number of Reviews']
    byPopularity.columns = cols
    byRating.columns = cols
    # display results
    st.write('Top',K,genre,'movies by popularity:')
    st.table(byPopularity.style.format({ 'Average Rating': '{:.2f}','Number of Reviews':'{:.0f}'}))
    #st.table(byPopularity)
    ('Top',K,genre,'movies by ratings:')
    st.table(byRating.style.format({ 'Average Rating': '{:.2f}','Number of Reviews':'{:.0f}'}))


# collaborative recommendation
elif radio == "Collaborative":
    ratings = pd.read_csv(ratingsFile,sep='::',header=None,engine='python',names=['UserID','MovieID','Rating','Timestamp'],index_col=False)
    movies = list(set(ratings['MovieID']))
    st.write("Please rate the following movies:")
    #left_column, right_column = st.columns(2)
    newRatings = np.zeros(10)
    for it in range(10):
        st.write("**"+top10['Title'][it]+"**  \n"+top10['Genres'][it])
        newRatings[it] = st.select_slider('',options=[1,2,3,4,5],key=it,value=3)
        st.write('---')
    if st.button('Get movie recommendations'):
        with st.spinner(text='Retrieving your movie recommendations...'):
            # load data
            df = pd.DataFrame([newuserID*np.ones(10),top10['MovieID'],newRatings],index=['UserID','MovieID','Rating']).T
            df2 = pd.concat([ratings[['UserID','MovieID','Rating']],df],axis=0,ignore_index=True)
            data = surprise.Dataset.load_from_df(df2, reader)
            trainset = data.build_full_trainset()
            # train model
            SVD.fit(trainset)
            # make predictions
            predRatings = []
            for movie in movies:
                predRatings.append(SVD.predict(newuserID,movie).est)
            idxsort = np.flipud(np.argsort(predRatings))
            top5idx = idxsort[:5]
            top5 = np.array(movies)[top5idx]
            # show recommendations
            st.write('Here are the recomendations based on your ratings:')
            for it in range(5):
                movieID = top5[it]
                idx = np.where(movieRatings['MovieID']==movieID)[0][0]
                st.write("**"+movieRatings['Title'][idx]+"**  \n"+movieRatings['Genres'][idx])
            

