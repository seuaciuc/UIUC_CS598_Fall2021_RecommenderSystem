import streamlit as st
import pickle

### INPUTS
MINREVIEW = 10
K = 5
genres = ['Action','Adventure','Animation',"Children's",'Comedy','Crime','Documentary','Drama','Fantasy',\
          'Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western']
pklfile = 'movieRatings.pkl'

# load file
fid = open(pklfile,'rb')
movieRatings = pickle.load(fid)
fid.close()

### FUNCTION TO OBTAIN THE RECOMMENDATIONS
def getGenderBasedRecommendations(movieRatings,genre,K):
    f = movieRatings[movieRatings[genre]==1] 
    byPopularity = f.sort_values(by=['nReviews','avgRating'],ascending=False, ignore_index=True)
    # add filter by number of reviews, sort by average rating
    f2 = f[f['nReviews']>=MINREVIEW] 
    byRating = f2.sort_values(by=['avgRating','nReviews'],ascending=False, ignore_index=True)
    return byPopularity[['Title','avgRating','nReviews']][0:K], byRating[['Title','avgRating','nReviews']][0:K]



### CREATE THE SIDE BAR FOR CHOICE OF RECOMMENDER SYSTEM
st.sidebar.title("Recommender Systems")
radio = st.sidebar.radio(label="Choose a system", options=["Genre-based", "Collaborative"])

### gender based recommendations
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
    st.write("This will be the collaborative system")

