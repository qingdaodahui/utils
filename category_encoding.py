import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import bisect
from collections import Counter


class labelencoder(LabelEncoder):
    """
    sklearn.preprocess.LabelEncoder can't process values which don't appear in fit label encoder.
    this method can process this problem. Replace all unknown values to a certain value, and encode this
    value to 0.

    Attributes
    ----------
    like sklearn.preprocess.LabelEncoder

    Example
    -------
    enc = labelencoder()
    enc.fit(['a','b','c'])
    enc.transform(['a','v','d'])
    Out: array([1, 0, 0])

    """

    def __init__(self):
        super(labelencoder, self).__init__()

    def fit(self, X, y=None):
        """
        :param X: array-like of shape (n_samples,)
        :param y: None
        :return:
        """
        l = list(np.unique(X))
        t1 = '<unknown>'
        t2 = -999
        while (t1 in l):
            t1 = t1 + '*'
        while (t2 in l):
            t2 -= t2

        le = LabelEncoder(**self.get_params())
        le.fit(X)

        le_classes = le.classes_.tolist()
        try:
            bisect.insort_left(le_classes, t1)
            self.unknown = t1
        except:
            bisect.insort_left(le_classes, t2)
            self.unknown = t2
        le.classes_ = le_classes
        self.encoder = le

    def transform(self, X):
        """
        :param X: array-like of shape (n_samples,)
        :return:
        """
        X = [s if s in self.encoder.classes_ else self.unknown for s in X]
        return self.encoder.transform(X)


class onehotencoder(OneHotEncoder):
    """
    sklearn.preprocess.OnehotEncoder only can process numerical values.
    this method can process str.

    Attributes
    ----------
    like sklearn.preprocess.OneHotEncoder

    Example
    -------
    enc = onehotencoder(sparse=False)
    enc.fit(['a','b','c'])
    enc.transform(['a','v','d'])
    Out:
    array([[ 1.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.]])


    """

    # def __init__(self):
    #     super(onehotencoder, self).__init__()

    def fit(self, X, y=None):
        """
        :param X: array-like of shape (n_samples,)
        :param y: None
        :return:
        """
        le = labelencoder()
        le.fit(X)
        self.le = le

        X = self.le.transform(X)

        # below codes can share the init params, but onehot will be not a instance.so will haven't its attributes.
        # onehot = OneHotEncoder
        # onehot.fit(self, X.reshape(-1, 1))
        # self.encoder.transform(self, X.reshape(-1, 1))

        onehot = OneHotEncoder(**self.get_params())
        onehot.fit(X.reshape(-1, 1))

        self.encoder = onehot

    def transform(self, X):
        """
        :param X: array-like of shape (n_samples,)
        :return:
        """
        X = self.le.transform(X)
        return self.encoder.transform(X.reshape(-1, 1))


class countencoder(object):
    """
    count encoding: Replace categorical variables with count in the train set.
    replace unseen variables with 1.

    Attributes
    ----------
    like sklearn.preprocess.OneHotEncoder

    Example
    -------
    enc = onehotencoder(sparse=False)
    enc.fit(['a','b','c'])
    enc.transform(['a','v','d'])
    Out:
    array([[ 1.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.]])


    """

    def __init__(self, unseen_values=1):
        self.unseen_values = 1

    def fit(self, X, y=None):
        """
        :param X: array-like of shape (n_samples,)
        :param y: None
        :return:
        """
        Counter(X)

    def transform(self, X):
        """
        :param X: array-like of shape (n_samples,)
        :return:
        """


# TODO: hashencoder

from sklearn.feature_extraction.text import CountVectorizer


class CategoryEncoder(object):
    def __init__(self, method='onehot'):
        self.method = method

    def fit(self, X, y=None):
        pass

    def transform(self, X):
        pass



from sklearn.base import TransformerMixin, BaseEstimator
import hashlib
class HashingEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.cols_set = []
        self.unknown_type = None

    def fit(self, X, col=None, n_components=5, hashing_method='md5'):
        """
        :param X: array-like of shape (n_samples,)
        :param y: None
        :return:
        """
        if n_components <= 0:
            raise ValueError('n_components shout be greater than 0.')

        if not col:
            col = [f'Hash_{_}' for _ in range(n_components)]
        self.col = col
        self.n_components = n_components
        self.hashing_method = hashing_method

        self.cols_set = list(np.unique(X))
        self.unknown_type = '<unknown>'
        while (self.unknown_type in self.cols_set):
            self.unknown_type += '*'
        return self

    def transform(self, X):
        """
        :param X: array-like of shape (n_samples,)
        :return:
        """
        X_tmp = [_  if _ in self.cols_set else self.unknown_type  for _ in X]
        X_tmp = pd.DataFrame(X_tmp, columns=[self.col])
        return self.__hash_col(X_tmp)
        

    def __hash_col(self, df):
        """
        :param df: dataframe of X
        return:
        """
        cols = [f'{self.col}_{i}' for i in range(self.n_components)]
        def xform(x):
            tmp = np.zeros(self.n_components)
            tmp[self.__hash(x) % self.n_components] = 1
            return pd.Series(tmp, index=cols).astype(int)
        df[cols] = df[self.col].apply(xform)
        return df.drop(self.col, axis=1)
    
    def __hash(self, string):
        if self.hashing_method == 'md5':
            return int(hashlib.md5(str(string).encode('utf-8')).hexdigest(), 16)
        else:
            raise ValueError('Hashing Method: %s Not Available. Please check that.' % self.hashing_method)


# 装饰器 - 输入和返回数据统一格式 
# TODO: transfer the output to the one-hot-encoder
class BinningEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.cut_points = []
        self.labels = None

    def fit(self, X, n_components=10, binning_method='cut', labels=None):
        """
        :param X: array-like of shape (n_samples,)
        :param n_components: the number of bins
        :param binning_method: the method of the bin
        :pabel labels:
        :return:
        """
        # 等频 qcut
        # 等宽 cut
        # 决策树 dt
        self.n_components = n_components
        self.binning_method = binning_method
        self.labels = labels
        if self.labels and len(self.labels) != self.n_components:
            raise ValueError('Bin labels must be one fewer than the number of bin edges.')

        if self.binning_method == 'cut':
            try:
                r = pd.cut(X, bins=self.n_components, retbins=True)
                self.cut_labels = r[0]._get_categories().to_native_types().tolist()
                self.cut_points = r[1].tolist()
            except:
                raise Exception('Error in pd.cut')
        elif self.binning_method == 'qcut':
            try:
                r = pd.qcut(data, q=np.linspace(0, 1, self.n_components), precision=0, retbins=True, labels=labels)
                self.cut_labels = r[0]._get_categories().to_native_types().tolist()
                self.cut_points = r[1].tolist()
            except:
                raise Exception('Error in pd.qcut')
        elif self.binning_method == 'dt':
            pass
        else:
            raise ValueError("binning_method: '%s' is not defined." % self.binning_method)
    
        if np.inf not in self.cut_points:
            self.cut_labels.append(f'(%s, inf]' % self.cut_points[-1])
            self.cut_points.append(np.inf)
        if -np.inf not in self.cut_points:
            self.cut_labels.insert(0, f'(-inf, %s]' % self.cut_points[0])
            self.cut_points.insert(0, -np.inf)


    def transform(self, X, one_hot=False):
        """
        :param X: array-like of shape (n_samples,)
        :param one_hot: return one_hot type of X or not
        :return:
        """
        if self.cut_points == []:
            raise ValueError('cut_points is empty.')
        try:
            r = pd.cut(X, bins=self.cut_points, labels=self.labels, retbins=True)[0]
        except:
            raise Exception('Error in pd.cut')
        if not one_hot:
            # labels = list(pd.Series(r.get_values()))                                            # interval type for sorting
            return pd.DataFrame([X, labels], index=['Number', 'Range']).T
        else:
            labels = r.astype(str).tolist()
            ohe_encoder = onehotencoder()
            ohe_encoder.fit(self.cut_labels)
            # cols = [f'Range_{self.cut_labels[i]}' for i in range(len(self.cut_labels))]         # for pd.DataFrame
            data = ohe_encoder.transform(labels)
            return data.toarray()


