class FeatureRegistry:

    def __init__(self):

        self.features = {}

    def register(self, name, func):

        self.features[name] = func

    def compute(self, df):

        df = df.copy()

        for name, func in self.features.items():

            df[name] = func(df)

        return df