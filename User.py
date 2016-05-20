from sklearn import linear_model
from sklearn.feature_extraction import DictVectorizer
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.pipeline import Pipeline

class User(object):
    """This class es used to store information about the users and do some data mining"""

    def _init_(self,name):
        self.name = name
        self.preferences = []
        self.ratings = {}
        self.history = []
    
    def get_tour_data(self, city_name = 'San_Francisco'):
        with open('Data/Tour_Data.json') as f:
                 data = json.load(f)

        tour_data = []

        for tour in [tour for tour in data['features'] if tour['geometry']['type'] == 'multiPoint'] and tour['properties']['city'] == city_name:

            this_tour={'city' : tour['properties']['city'], 'rating' : tour['properties']['rating'], 'duration' : tour['properties']['duration'], 'start_time' : tour['properties']['start_time'] ,
                              'buss_names' : tour['properties']['buss_names'], 'buss_types' : tour['properties']['buss_types']}

            for buss_name in tour['properties']['buss_names']:
                this_tour[buss_name] = 1

            for buss_type in tour['properties']['buss_types'].keys():
                this_tour[buss_type] = tour['properties']['buss_types'][buss_type]

            tour_data.append(this_tour)

        return tour_data

    def predict(tour_data):

        vec = DictVectorizer()

        tour_data = get_tour_data()

        transformed = vec.fit_transform(tour_data).toarray()
        categories = vec.get_feature_names()

        y = transformed[:,[categories.index('rating')]]
        X = transformed[:,np.arange(transformed.shape[1])!=categories.index('rating')]

        reg_tree = DecisionTreeRegressor()

        addboost_tree = AdaBoostRegressor(DecisionTreeRegressor(max_depth=4),
                              n_estimators=300, random_state=rng)

        red_tree.fit(X,y)
        addboost_tree(X,y)

        # Predict
        y_1 = red_tree.predict(X)
        y_2 = addboost_tree.predict(X)

        return prediction







